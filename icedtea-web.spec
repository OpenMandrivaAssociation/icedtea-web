%ifarch %{ix86} x86_64
%if "%{distepoch}" >= "2015.0"
  %define javaver	1.8.0
  %define priority	18000
%else
  %define javaver	1.7.0
  %define priority	17000
%endif
%else
  %define javaver	1.6.0
  %define priority	16000
%endif

%ifarch %{ix86}
  %define archinstall	i386
%endif
%ifarch x86_64
  %define archinstall	amd64
%endif

%define javadir	%{_jvmdir}/java-openjdk
%define jredir	%{_jvmdir}/jre-openjdk
%define javaplugin	libjavaplugin.so
%ifarch x86_64
  %define javaplugin	libjavaplugin.so.%{_arch}
%endif

%define binsuffix      .itweb

Summary:	Additional Java components for OpenJDK
Name:		icedtea-web
Version:	1.5.2
Release:	1
Group:		Networking/WWW
License:	LGPLv2+ and GPLv2 with exceptions
Url:		http://icedtea.classpath.org/wiki/IcedTea-Web
Source0:	http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz

# IcedTea is only built on these archs for now
ExclusiveArch:	x86_64 i586

BuildRequires:	desktop-file-utils
BuildRequires:	zip
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
%ifarch %{ix86} x86_64
BuildRequires:	java-%{javaver}-openjdk-devel
%else
BuildRequires:	java-%{javaver}-openjdk-devel >= 1.6.0.0-18.b22
%endif
BuildRequires:	pkgconfig(mozilla-plugin)
BuildRequires:	pkgconfig(zlib)

Requires:	java-%{javaver}-openjdk
Requires(post,postun):	update-alternatives

# Standard JPackage plugin provides.
Provides:	java-plugin = %{javaver}
Provides:	java-1.6.0-openjdk-plugin = 1.6.0.0-18.b22
Obsoletes:	java-1.6.0-openjdk-plugin

%description
The IcedTea-Web project provides a Java web browser plugin, an implementation
of Java Web Start (originally based on the Netx project) and a settings tool to
manage deployment settings for the aforementioned plugin and Web Start
implementations.

%package	javadoc
Summary:	API documentation for IcedTea-Web

Requires:	jpackage-utils
BuildArch:	noarch

%description javadoc
This package contains Javadocs for the IcedTea-Web project.

%prep
export LC_ALL=en_US.UTF-8
%setup -q

# ugly hack to make it work on 2009.0/mes5 (pcpa)
sed -e 's|AC_CANONICAL_HOST||;' -i configure.*
autoreconf -fi

%build
%configure \
	--with-pkgversion=%{_vendor}-%{release}-%{_arch} \
	--docdir=%{_javadocdir}/%{name} \
	--with-jdk-home=%{javadir} \
	--with-jre-home=%{jredir} \
	--program-suffix=%{binsuffix}

%make CXXFLAGS="%{optflags}"

%install
%makeinstall_std
# Move javaws man page to a more specific name
mv %{buildroot}%{_mandir}/man1/javaws.1 %{buildroot}%{_mandir}/man1/javaws-itweb.1

# Install desktop files.
install -d -m755 %{buildroot}%{_datadir}/{applications,pixmaps}
cp javaws.png %{buildroot}%{_datadir}/pixmaps
desktop-file-install --vendor ''\
	--dir %{buildroot}%{_datadir}/applications javaws.desktop
desktop-file-install --vendor ''\
	--dir %{buildroot}%{_datadir}/applications itweb-settings.desktop

%post
if [ $1 -gt 1 ]
then
update-alternatives --remove %{javaplugin} \
	%{jre6dir}/lib/%{archinstall}/IcedTeaPlugin.so 2>/dev/null || :	
fi

%posttrans
update-desktop-database &> /dev/null || :
update-alternatives \
	--install %{_libdir}/mozilla/plugins/libjavaplugin.so %{javaplugin} \
	%{_libdir}/IcedTeaPlugin.so %{priority} \
	--slave %{_bindir}/javaws javaws %{_prefix}/bin/javaws%{binsuffix} \
	--slave %{_mandir}/man1/javaws.1.gz javaws.1.gz \
	%{_mandir}/man1/javaws-itweb.1.gz

exit 0

%postun
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ]; then
	update-alternatives --remove %{javaplugin} \
		%{_libdir}/IcedTeaPlugin.so
fi

exit 0

%files
%{_bindir}/*
%{_libdir}/IcedTeaPlugin.so
%{_datadir}/applications/*
%{_datadir}/icedtea-web
%{_datadir}/pixmaps/*
%{_mandir}/man1/*
%doc NEWS README COPYING

%files javadoc
%{_javadocdir}/%{name}
%doc COPYING

