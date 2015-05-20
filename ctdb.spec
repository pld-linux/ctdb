# TODO
# - skip interfaces check:
#   checking for iface getifaddrs...
#   lo         IP=127.0.0.1 NETMASK=255.0.0.0
#   eth0       IP=x.x.x.x NETMASK=255.255.252.0
# - add support for /sbin/ss instead of /bin/netstat (ss uses kernel netlink
#   which is huge win on server with loads of open tcp sockets)
# - patch scripts for pld
#
# Conditional build:
%bcond_without	ibverbs		# InfiniBand support
%bcond_without	pcp		# Performance Co-Pilot support
#
Summary:	A Clustered Database based on Samba's Trivial Database (TDB)
Summary(pl.UTF-8):	Klastrowa baza danych oparta na bazie danych Trivial Database z Samby (TDB)
Name:		ctdb
Version:	2.5.5
Release:	1
License:	GPL v3+
Group:		Daemons
Source0:	https://www.samba.org/ftp/ctdb/%{name}-%{version}.tar.gz
# Source0-md5:	fae1131a07a12e4db1cdb01a81aa1981
Patch0:		%{name}-format.patch
URL:		http://ctdb.samba.org/
%{?with_pcp:BuildRequires:	pcp-devel}
BuildRequires:	popt-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	talloc-devel
BuildRequires:	tdb-devel
BuildRequires:	tevent-devel
%if %{with ibverbs}
BuildRequires:	libibverbs-devel
BuildRequires:	librdmacm-devel
%endif
Requires(post,preun):	/sbin/chkconfig
Requires:	coreutils
Requires:	psmisc
Requires:	rc-scripts
Requires:	sed
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
CTDB is a cluster implementation of the TDB database used by Samba and
other projects to store temporary data. If an application is already
using TDB for temporary data it is very easy to convert that
application to be cluster aware and use CTDB instead.

%description -l pl.UTF-8
CTDB to klastrowa implementacja bazy danych TDB używanej w Sambie oraz
innych projektach do przechowywania danych tymczasowych. Jeśli jakaś
aplikacja już wykorzystuje TDB do trzymania danych tymczasowych,
bardzo przerobić ją na klastrowalną, wykorzystującą CTDB.

%package devel
Summary:	CTDB clustered database development package
Summary(pl.UTF-8):	Pakiet programistyczny klastrowej bazy danych CTDB
Group:		Development/Libraries
Requires:	tdb-devel
# does not require base

%description devel
Header files etc. you can use to develop CTDB applications.

%description devel -l pl.UTF-8
Pliki nagłówkowe i inne, przy użyciu których można tworzyć aplikacje
wykorzystujące CTDB.

%package -n pcp-ctdb
Summary:	CTDB PMDA
Summary(pl.UTF-8):	PMDA CTDB
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	pcp

%description -n pcp-ctdb
This PMDA extracts metrics from the locally running ctdbd daemon for
export to PMCD.

%description -n pcp-ctdb -l pl.UTF-8
Ten PMDA odczytuje pomiary z lokalnie działającego demona ctdbd w celu
wyeksportowania do PMCD.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	%{?with_pcp:--enable-pmda} \
	%{?with_ibverbs:--enable-infiniband}
%{__make} showflags
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp -a config/ctdb.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/ctdb
install -p config/ctdb.init $RPM_BUILD_ROOT/etc/rc.d/init.d/ctdb
cp -p config/ctdb.service $RPM_BUILD_ROOT%{systemdunitdir}
install -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/ctdb.conf <<EOF
d /var/run/ctdb 0755 root root -
EOF

install -d $RPM_BUILD_ROOT%{_docdir}/ctdb/tests/bin
install -p tests/bin/ctdb_transaction $RPM_BUILD_ROOT%{_docdir}/ctdb/tests/bin

# Remove "*.old" files
find $RPM_BUILD_ROOT -name "*.old" -exec rm -fv {} ';'

# fix doc path
mv $RPM_BUILD_ROOT%{_docdir}/ctdb $RPM_BUILD_ROOT%{_docdir}/ctdb-%{version}
cp -a web $RPM_BUILD_ROOT%{_docdir}/ctdb-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ctdb
%service ctdb restart

%preun
if [ "$1" -eq "0" ] ; then
	%service ctdb stop
	/sbin/chkconfig --del ctdb
fi

%files
%defattr(644,root,root,755)
%{_docdir}/ctdb-%{version}
%dir %{_sysconfdir}/ctdb
%{_sysconfdir}/ctdb/events.d
%{_sysconfdir}/ctdb/nfs-rpc-checks.d
%{_sysconfdir}/ctdb/notify.d
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/ctdb-crash-cleanup.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/debug-hung-script.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/debug_locks.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/gcore_trace.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/notify.sh
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ctdb/functions
%{_sysconfdir}/ctdb/statd-callout
%attr(755,root,root) %{_sbindir}/ctdbd
%attr(755,root,root) %{_sbindir}/ctdbd_wrapper
%attr(755,root,root) %{_bindir}/ctdb
%attr(755,root,root) %{_bindir}/ctdb_diagnostics
%attr(755,root,root) %{_bindir}/ctdb_event_helper
%attr(755,root,root) %{_bindir}/ctdb_lock_helper
%attr(755,root,root) %{_bindir}/ltdbtool
%attr(755,root,root) %{_bindir}/onnode
%attr(755,root,root) %{_bindir}/ping_pong
%attr(755,root,root) %{_bindir}/smnotify
%{systemdunitdir}/ctdb.service
%{systemdtmpfilesdir}/ctdb.conf
%attr(754,root,root) /etc/rc.d/init.d/ctdb
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ctdb
%attr(440,root,root) /etc/sudoers.d/ctdb
%dir /var/run/ctdb
%{_mandir}/man1/ctdb.1*
%{_mandir}/man1/ctdbd.1*
%{_mandir}/man1/ctdbd_wrapper.1*
%{_mandir}/man1/ltdbtool.1*
%{_mandir}/man1/onnode.1*
%{_mandir}/man1/ping_pong.1*
%{_mandir}/man5/ctdbd.conf.5*
%{_mandir}/man7/ctdb.7*
%{_mandir}/man7/ctdb-statistics.7*
%{_mandir}/man7/ctdb-tunables.7*

%files devel
%defattr(644,root,root,755)
%{_includedir}/ctdb*.h
%{_pkgconfigdir}/ctdb.pc

%files -n pcp-ctdb
%defattr(644,root,root,755)
%dir /var/lib/pcp/pmdas/ctdb
%doc /var/lib/pcp/pmdas/ctdb/README
%attr(755,root,root) /var/lib/pcp/pmdas/ctdb/Install
%attr(755,root,root) /var/lib/pcp/pmdas/ctdb/Remove
%attr(755,root,root) /var/lib/pcp/pmdas/ctdb/pmdactdb
/var/lib/pcp/pmdas/ctdb/domain.h
/var/lib/pcp/pmdas/ctdb/help
/var/lib/pcp/pmdas/ctdb/pmns
