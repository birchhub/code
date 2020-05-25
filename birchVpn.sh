#!/bin/bash

EASYRSADIR=/home/user/EasyRSA-3.0.7/
CONFDIR=~/birchVpn

function setupPKI() {
	[ ${#} -lt 1 ] && return 1
	local CACN=${1}

	${EASYRSADIR}/easyrsa init-pki
	EASYRSA_REQ_CN=${CACN} ${EASYRSADIR}/easyrsa --batch build-ca nopass
	EASYRSA_CRL_DAYS=3650 ${EASYRSADIR}/easyrsa gen-crl

	return 0
}

function createServerCertificateReq() {
	[ ${#} -lt 1 ] && return 1
	local SERVERNAME=${1}

	EASYRSA_REQ_CN=${SERVERNAME} ${EASYRSADIR}/easyrsa --batch gen-req ${SERVERNAME} nopass

	return 0
}

function signServerCertificate() {
	[ ${#} -lt 1 ] && return 1
	local SERVERNAME=${1}

	${EASYRSADIR}/easyrsa sign-req server ${SERVERNAME}
	
	return 0
}

function setupServer() {
	[ ${#} -lt 1 ] && return 1
	local SERVERNAME=${1}

	# create and add server certificate
	createServerCertificateReq ${SERVERNAME}
	signServerCertificate ${SERVERNAME}

	[ -d /etc/openvpn/server ] || mkdir -p /etc/openvpn/server

	cp pki/ca.crt /etc/openvpn/

	cp pki/private/${SERVERNAME}.key /etc/openvpn/server/
	cp pki/issued/${SERVERNAME}.crt /etc/openvpn/server/
	cp pki/crl.pem /etc/openvpn/crl.pem

	# add HAMC for ALL handshake messages
	openvpn --genkey --secret /etc/openvpn/tls-crypt.key

	# Generate server.conf
	echo "port 1140
proto udp
dev tun
user nobody
group nogroup
persist-key
persist-tun
keepalive 10 120
topology subnet
server 10.76.76.0 255.255.255.0
push route 10.100.100.0 255.255.255.0
ifconfig-pool-persist ipp.txt
dh none
ecdh-curve prime256v1
tls-crypt tls-crypt.key
crl-verify crl.pem
ca ca.crt
cert server/${SERVERNAME}.crt
key server/${SERVERNAME}.key
auth SHA256
cipher AES-128-GCM
ncp-ciphers AES-128-GCM
tls-server
tls-version-min 1.2
tls-cipher TLS-ECDHE-ECDSA-WITH-AES-128-GCM-SHA256
client-config-dir /etc/openvpn/ccd
status /var/log/openvpn/status.log
verb 3" >/etc/openvpn/server.conf

	mkdir -p /etc/openvpn/ccd
	mkdir -p /var/log/openvpn
}

function setupDone() {
	SYSTEMDUNIT="birchvpn"
	systemctl status ${SYSTEMDUNIT} > /dev/null 2>&1 && return 0 || return 1
}

function setup() {
	setupDone && {
		echo "Setup already executed"
		return 1
	}

	[ -d ${CONFDIR} ] || mkdir -p ${CONFDIR}
	pushd ${CONFDIR}

	# create hints file for easy-rsa
	#echo 'set_var EASYRSA_DN		"cn-only"' > ${CONFDIR}/vars
	echo 'set_var EASYRSA_ALGO		"ec"' > ${CONFDIR}/vars
	echo 'set_var EASYRSA_CURVE		"prime256v1"' >> ${CONFDIR}/vars
	
	export EASYRSA_VARS_FILE="${CONFDIR}/vars"

	ORG="birchhub"
	setupPKI "CA-${ORG}" || {
		echo "error setting up PKI"
		popd
		return 1
	}
	setupServer "srv-${ORG}" || {
		echo "error creating server certificate"
		popd
		return 1
	}

	cat > serverSettings.conf << EOF
CONFIP=192.168.100.132
CONFSERVERCN=srv-${ORG}
EOF

	popd
}


function createClientCertificateReq() {
	[ ${#} -lt 1 ] && return 1
	local CLIENTNAME=${1}

	EASYRSA_REQ_CN=${CLIENTNAME} ${EASYRSADIR}/easyrsa --batch gen-req "clt-${CLIENTNAME}" nopass
	return 0
}

function signClientCertificate() {
	[ ${#} -lt 1 ] && return 1
	local CLIENTNAME=${1}

	${EASYRSADIR}/easyrsa --batch sign-req client "clt-${CLIENTNAME}"
}

function addClient() {
	[ ${#} -lt 1 ] && return 1
	local CLIENTNAME=${1}

	pushd ${CONFDIR}
	createClientCertificateReq ${CLIENTNAME} || {
		echo "Not able to create client certificate request"
		popd
		return 1
	}
	signClientCertificate ${CLIENTNAME} || {
		echo "Not able to sign client certificate"
		popd
		return 1
	}

	[ -d clients ] || mkdir clients
	source serverSettings.conf
	cat > clients/clt_${CLIENTNAME}.ovpn << EOF
client
proto udp
explicit-exit-notify
remote ${CONFIP} 1140
dev tun
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
verify-x509-name ${CONFSERVERCN} name
auth SHA256
auth-nocache
cipher AES-128-GCM
tls-client
tls-version-min 1.2
tls-cipher TLS-ECDHE-ECDSA-WITH-AES-128-GCM-SHA256
ignore-unknown-option block-outside-dns
setenv opt block-outside-dns 
verb 3
EOF

	echo "<ca>" >> clients/clt_${CLIENTNAME}.ovpn
	cat pki/ca.crt >> clients/clt_${CLIENTNAME}.ovpn
	echo "</ca>" >> clients/clt_${CLIENTNAME}.ovpn

	echo "<cert>" >> clients/clt_${CLIENTNAME}.ovpn
	openssl x509 -in pki/issued/clt-${CLIENTNAME}.crt >> clients/clt_${CLIENTNAME}.ovpn
	echo "</cert>" >> clients/clt_${CLIENTNAME}.ovpn
	echo "<key>" >> clients/clt_${CLIENTNAME}.ovpn
	cat pki/private/clt-${CLIENTNAME}.key >> clients/clt_${CLIENTNAME}.ovpn
	echo "</key>" >> clients/clt_${CLIENTNAME}.ovpn
	echo "<tls-crypt>" >> clients/clt_${CLIENTNAME}.ovpn
	cat /etc/openvpn/tls-crypt.key >> clients/clt_${CLIENTNAME}.ovpn
	echo "</tls-crypt>" >> clients/clt_${CLIENTNAME}.ovpn

	popd
	return 0
}

function usage() {
	echo "birchvpn openvpn configuratior"
	echo ""
	echo "birchvpn setup [easydir]"
	echo "birchvpn adduser username [easydir]"
}

function cmderror() {
	usage
	exit 1
}

function precheck() {
	[ -d ${EASYRSADIR} ] ||  {
		echo "install easy-rsa into ${EASYRSADIR}"
		exit 2
	}

	return 0
}

[ ${#} -lt 1 ] && cmderror
if [[ ${1} == "setup" ]]; then
	[[ ${2} != "" ]] && EASYRSADIR=${2}

	precheck
	setup
elif [[ ${1} == "adduser" ]]; then
	[ ${#} -lt 2] && cmderror
	[[ ${3} != "" ]] && EASYDIR=${2}

	USERNAME=${2}
	precheck
	# XXX check if setup exists
	addClient ${USERNAME}
fi

#/usr/sbin/openvpn   --status /run/openvpn/server.status 10 --cd /etc/openvpn --script-security 2 --config /etc/openvpn/server.conf --writepid /run/openvpn/server.pid
# XXX set ip via argument
# check FW rules
# ip_forward
