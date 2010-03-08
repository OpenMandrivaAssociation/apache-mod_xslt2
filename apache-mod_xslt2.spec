#Module-Specific definitions
%define snap 2004112100
%define mod_name mod_xslt2
%define mod_conf 25_%{mod_name}.conf
%define mod_so mod_xslt.so

%define	major 0
%define libname	%mklibname modxslt %{major}

%define epoch 1

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	1.3.8
Release:	%mkrel 1.%{snap}.15
Group:		System/Servers
License:	GPL
URL:		http://www.mod-xslt2.com/
Source0:	modxslt-%{snap}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		modxslt-2004101700-no_root_check.diff
Patch1:		modxslt-2004112100-apache220.diff
Patch2:		modxslt-2004112100-apr1x.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	libxml2-devel
BuildRequires:	libxslt-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	file
Provides:	apache-mod_xslt = %{epoch}:%{version}-%{release}
Obsoletes:	apache-mod_xslt
Epoch:		%{epoch}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod-xslt2 is a server side module able to apply stylesheets to xml
data on the fly. mod-xslt2 as it is today is almost a complete
rewrite of the original mod-xslt2 written by Philipp Dunkel, with
many new features added and a complete code clean up. mod-xslt2 is
Free Software, as it will always be, it is released under the
terms of the GPL and anybody is welcome to join its development. 

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:          System/Libraries

%description -n	%{libname}
Shared libraries for %{name}

%package -n	%{libname}-devel
Summary:	Development library and header files for the %{name} library
Group:		Development/C
Requires:	%{libname} = %{epoch}:%{version}-%{release}
Provides:	%{name}-devel libmodxslt-devel
Obsoletes:	%{name}-devel libmodxslt-devel

%description -n	%{libname}-devel
This package contains the static %{libname} library and its header
files.

%prep

%setup -q -n modxslt-%{snap}
%patch0 -p1
%patch1 -p0
%patch2 -p0

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export WANT_AUTOCONF_2_5=1
libtoolize --copy --force; aclocal-1.7; autoconf

%configure2_5x --localstatedir=/var/lib \
    --with-sapi=apache2 \
    --with-apxs=%{_sbindir}/apxs \
    --with-apr-config=%{_bindir}/apr-1-config \
    --with-apu-config=%{_bindir}/apu-1-config

%make


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

%makeinstall_std

mv %{buildroot}%{_libdir}/apache %{buildroot}%{_libdir}/apache-extramodules

# re-define version, rpm is so stupid...

bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

# do we need these?
rm -f %{buildroot}%{_bindir}/modxslt-parse
rm -f %{buildroot}%{_bindir}/modxslt-perror

# cleanup docs
find doc -name "Makefile*" | xargs rm -f

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CREDITS LICENSE README
%doc doc/manual/manual doc/xslt/*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*

%files -n %{libname}
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/libmodxslt*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%doc TODO
%doc doc/dev/*
%attr(0755,root,root) %{_bindir}/modxslt-config
%attr(0755,root,root) %{_libdir}/*.a
%attr(0644,root,root) %{_libdir}/*.la
%attr(0755,root,root) %{_libdir}/*.so
%{_includedir}/modxslt*
%{_mandir}/man1/*


