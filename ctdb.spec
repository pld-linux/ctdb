# TODO
# - pcp support (pcp/{pmapi,impl,pmda}.h)
# - shared libctdb (not ready in Makefile)
# - skip interfaces check:
#   checking for iface getifaddrs...
#   lo         IP=127.0.0.1 NETMASK=255.0.0.0
#   eth0       IP=x.x.x.x NETMASK=255.255.252.0
# - patch scripts for pld
#
# Conditional build:
%bcond_without	ibverbs		# InfiniBand support
#
Summary:	A Clustered Database based on Samba's Trivial Database (TDB)
Summary(pl.UTF-8):	Klastrowa baza danych oparta na bazie danych Trivial Database z Samby (TDB)
Name:		ctdb
Version:	2.0
Release:	1
License:	GPL v3+
Group:		Daemons
Source0:	http://www.samba.org/ftp/ctdb/%{name}-%{version}.tar.gz
# Source0-md5:	89a397e165e7f5347f06a6cf45fd6b60
Patch0:		%{name}-ib.patch
URL:		http://ctdb.samba.org/
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

%prep
%setup -q
%patch0 -p1

%build
%configure \
	%{?with_ibverbs:--enable-infiniband}
%{__make} showflags
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp -a config/ctdb.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/ctdb
install -p config/ctdb.init $RPM_BUILD_ROOT/etc/rc.d/init.d/ctdb

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
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/ctdb-crash-cleanup.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/debug-hung-script.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/gcore_trace.sh
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/notify.sh
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ctdb/functions
%{_sysconfdir}/ctdb/statd-callout
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ctdb
%attr(754,root,root) /etc/rc.d/init.d/ctdb
%attr(755,root,root) %{_sbindir}/ctdbd
%attr(755,root,root) %{_bindir}/ctdb
%attr(755,root,root) %{_bindir}/ctdb_diagnostics
%attr(755,root,root) %{_bindir}/ltdbtool
%attr(755,root,root) %{_bindir}/onnode
%attr(755,root,root) %{_bindir}/ping_pong
%attr(755,root,root) %{_bindir}/smnotify
%{_mandir}/man1/ctdb.1*
%{_mandir}/man1/ctdbd.1*
%{_mandir}/man1/ltdbtool.1*
%{_mandir}/man1/onnode.1*
%{_mandir}/man1/ping_pong.1*

%files devel
%defattr(644,root,root,755)
%{_libdir}/libctdb.a
%{_includedir}/ctdb*.h
%{_pkgconfigdir}/ctdb.pc
