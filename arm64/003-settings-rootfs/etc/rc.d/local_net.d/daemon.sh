#!/bin/sh

lcon=/opt/scripts/files/lcon
lconc=/opt/scripts/files/lconc
rcon=/opt/scripts/files/rcon
rconc=/opt/scripts/files/rconc
config="`grep ^kiosk_config= $lcon 2>/dev/null | head -n1 | cut -d= -f2-`"
PTH=/usr/share/icons/oxygen/22x22
pcid=`grep ^ID: /etc/version | cut -d' ' -f2`
wget="wget --no-http-keep-alive --no-cache --no-check-certificate"

if [ -e "$lcon" ]; then
(
    # Extract local config:
    grep -v '^daemon_' $lcon > $lconc
    # Sleep first:
    sleep "`grep ^daemon_check= $lcon 2>/dev/null | head -n1 | cut -d= -f2-`"m
    while true; do
	# Setup proxy:
	if [ -e /opt/scripts/proxy.pac ]; then
	    proxyc=`pactester -p /opt/scripts/proxy.pac -u $config | cut -d" " -f2-`
	    [ "$proxyc" = DIRECT ] && unset http_proxy https_proxy ftp_proxy || export http_proxy="http://$proxyc" https_proxy="http://$proxyc" ftp_proxy="http://$proxyc"
	fi
	# Download config with PC ID appended but not from FTP sites:
	[ "`echo $config | cut -c1-6`" = "ftp://" ] || config="$config?kiosk=$pcid"
	sleep 1; TRIES=14
	while [ $TRIES -gt 0 ]; do $wget -q -T20 -t1 --spider $config && break || { TRIES=$((TRIES-1)); sleep 2; }; done
	dat=`date '+%Y-%m-%d_%H:%M:%S'`
	fetch_config() { $wget -T20 -t3 -q -O /root/config-$dat $config; cp -a /root/config-$dat /root/config; fromdos /root/config; fromdos /root/config; fromdos /root/config; tr -dc "[:alnum:][:space:][:punct:]" < /root/config > /tmp/conf; sed -i 's/^ .*//' /tmp/conf; mv /tmp/conf $rcon; }
	fetch_config
	grep -q ^kiosk_config= $rcon 2>/dev/null || fetch_config
	grep -q ^kiosk_config= $rcon 2>/dev/null || fetch_config
	# Reset proxy (if applies):
	. /etc/profile.d/proxy.sh
	# Handle GLOBAL configs:
	if grep -q '^\[\[.*GLOBAL.*\]\]' $rcon; then
	    sed -n '/^\[\[.*'$pcid'.*\]\]/,/^$/p' $rcon | egrep -v '^\[|^\#|^$' > /tmp/conf
	    sed -e '/^\[\[.*GLOBAL.*\]\]/d' -e '/^\[\[/q' $rcon | egrep -v '^\[|^\#|^$' >> /tmp/conf
	    mv /tmp/conf $rcon
	else
	    sed -i '/^$/d' $rcon
	fi
	# Perform check only if config is sane:
	if grep -q ^kiosk_config= $rcon; then
	    # Extract remote config if it was downloaded correctly:
	    grep -q ^kiosk_config= $rcon && egrep -v '^daemon_|^burn_dev=|^md5conf=' $rcon > $rconc
	    # Cleanup first:
	    dunstify -C 745; killall greyos_reboot
	    if [ `md5sum $lconc | cut -d" " -f1` != `md5sum $rconc | cut -d" " -f1` ]; then
		[ "`grep ^daemon_force_reboot=yes $rcon`" ] && { dunstify -r 745 -u critical -i $PTH/status/dialog-information.png "System maintenance - PC will be restarted in 30 seconds ..."; sleep 30; init 6; }
		message="`grep ^daemon_message= $rcon 2>/dev/null | head -n1 | cut -d= -f2-`"
		[ "$message" ] && dunstify -r 745 -u critical -i $PTH/status/dialog-information.png "$message"
		/opt/scripts/files/greyos_reboot &
	    else
		message="`grep ^daemon_message= $rcon 2>/dev/null | head -n1 | cut -d= -f2-`"
		[ "$message" ] && dunstify -r 745 -u critical -i $PTH/status/dialog-information.png "$message"
	    fi
	    [ "`grep ^daemon_check= $rcon`" ] && sleep "`grep ^daemon_check= $rcon 2>/dev/null | head -n1 | cut -d= -f2-`"m || sleep 5m
	else
	    sleep 5m
	fi
    done
) &
fi
