%ifarch %{ix86} x86_64
  %define javaver	1.6.0
  %define priority	16000
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

%ifarch x86_64
  %define javadir	%{_jvmdir}/java-%{javaver}-openjdk.%{_arch}
  %define jredir	%{_jvmdir}/jre-%{javaver}-openjdk.%{_arch}
  %define javaplugin	libjavaplugin.so.%{_arch}
%else
  %define javadir	%{_jvmdir}/java-%{javaver}-openjdk
  %define jredir	%{_jvmdir}/jre-%{javaver}-openjdk
  %define javaplugin	libjavaplugin.so
%endif

%define binsuffix      .itweb

Name:		icedtea-web
Version:	1.1.5
%define subrel 1
Release:	%mkrel 0
Summary:	Additional Java components for OpenJDK
Group:		Networking/WWW
License:	LGPLv2+ and GPLv2 with exceptions
URL:		http://icedtea.classpath.org/wiki/IcedTea-Web
Source0:	http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz

BuildRequires:	desktop-file-utils
BuildRequires:	glib2-devel
BuildRequires:	gtk2-devel

%ifarch %{ix86} x86_64
BuildRequires:	java-%{javaver}-openjdk-devel
%else
BuildRequires:	java-%{javaver}-openjdk-devel >= 1.6.0.0-18.b22
%endif

BuildRequires:	xulrunner-devel
BuildRequires:	zip
BuildRequires:	zlib-devel

Requires:	java-%{javaver}-openjdk
Requires(post):   update-alternatives
Requires(postun): update-alternatives

# Standard JPackage plugin provides.
Provides:	java-plugin = %{javaver}

Provides:	java-1.6.0-openjdk-plugin = 1.6.0.0-18.b22
Obsoletes:	java-1.6.0-openjdk-plugin

# IcedTea is only built on these archs for now
ExclusiveArch:	x86_64 i586

Patch0:		icedtea-web-1.0.2-mutex_and_leak.patch

%description
The IcedTea-Web project provides a Java web browser plugin, an implementation
of Java Web Start (originally based on the Netx project) and a settings tool to
manage deployment settings for the aforementioned plugin and Web Start
implementations. 

%package javadoc
Summary:    API documentation for IcedTea-Web
Group:      Networking/WWW
Requires:   jpackage-utils
%if %mdkversion >= 201010
BuildArch:	noarch
%endif

%description javadoc
This package contains Javadocs for the IcedTea-Web project.

%prep
%setup -q

%patch0 -p1

%build
%configure2_5x						\
	--with-pkgversion=mandriva-%{release}-%{_arch}	\
	--docdir=%{_javadocdir}/%{name}			\
	--with-jdk-home=%{javadir}			\
	--with-jre-home=%{jredir}			\
	--libdir=%{_libdir}				\
	--program-suffix=%{binsuffix}			\
	--prefix=%{_prefix}

make CXXFLAGS="%{optflags}"

%install
%makeinstall_std
# Move javaws man page to a more specific name
mv %{buildroot}/%{_mandir}/man1/javaws.1 %{buildroot}/%{_mandir}/man1/javaws-itweb.1

# Install desktop files.
install -d -m 755 %{buildroot}%{_datadir}/{applications,pixmaps}
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
if [ $1 -eq 0 ]
then
  update-alternatives --remove %{javaplugin} \
    %{_libdir}/IcedTeaPlugin.so
fi

exit 0

%files
%defattr(-,root,root,-)
%{_prefix}/bin/*
%{_libdir}/IcedTeaPlugin.so
%{_datadir}/applications/*
%{_datadir}/icedtea-web
%{_datadir}/man/man1/*
%{_datadir}/pixmaps/*
%doc NEWS README COPYING

%files javadoc
%defattr(-,root,root,-)
%{_datadir}/javadoc/%{name}
%doc COPYING


