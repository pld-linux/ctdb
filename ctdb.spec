# TODO
# - skip interfaces check:
#   checking for iface getifaddrs...
#   lo         IP=127.0.0.1 NETMASK=255.0.0.0
#   eth0       IP=x.x.x.x NETMASK=255.255.252.0
# - add support for /sbin/ss instead of /bin/netstat (ss uses kernel netlink
#   which is huge win on server with loads of open tcp sockets)
# - patch scripts for pld
Summary:	A Clustered Database based on Samba's Trivial Database (TDB)
Summary(pl.UTF-8):	Klastrowa baza danych oparta na bazie danych Trivial Database z Samby (TDB)
Name:		ctdb
Version:	1.0.113
Release:	1
License:	GPL v3+
Group:		Daemons
URL:		http://ctdb.samba.org/
# Tarfile created using git
# git clone git://git.samba.org/sahlberg/ctdb.git ctdb
# cd ctdb
# git-archive --format=tar --prefix=%{name}-%{version}/ %{name}-%{version} | bzip2 > %{name}-%{version}.tar.bz2
Source0:	%{name}-%{version}.tar.bz2
# Source0-md5:	ce3eda943bf81c7c9e513ec715f4a785
BuildRequires:	autoconf >= 2.50
BuildRequires:	net-tools
BuildRequires:	popt-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	coreutils
Requires:	psmisc
Requires:	rc-scripts
Requires:	sed
Requires:	tdb
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
# does not require base

%description devel
Header files etc. you can use to develop CTDB applications.

%description devel -l pl.UTF-8
Pliki nagłówkowe i inne, przy użyciu których można tworzyć aplikacje
wykorzystujące CTDB.

%prep
%setup -q

%build
sh -x ./autogen.sh

CFLAGS="%{rpmcflags} $EXTRA -D_GNU_SOURCE -DCTDB_VERS=\"%{version}-%{release}\""
%configure
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
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) %{_sysconfdir}/ctdb/notify.sh
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ctdb/functions
%{_sysconfdir}/ctdb/statd-callout
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ctdb
%attr(754,root,root) /etc/rc.d/init.d/ctdb
%attr(755,root,root) %{_sbindir}/ctdbd
%attr(755,root,root) %{_bindir}/ctdb
%attr(755,root,root) %{_bindir}/smnotify
%attr(755,root,root) %{_bindir}/ping_pong
%attr(755,root,root) %{_bindir}/ctdb_diagnostics
%attr(755,root,root) %{_bindir}/onnode
%{_mandir}/man1/ctdb.1*
%{_mandir}/man1/ctdbd.1*
%{_mandir}/man1/onnode.1*

%files devel
%defattr(644,root,root,755)
%{_includedir}/ctdb.h
%{_includedir}/ctdb_private.h
%{_pkgconfigdir}/ctdb.pc
