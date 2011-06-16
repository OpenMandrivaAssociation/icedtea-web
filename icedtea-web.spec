%if %mandriva_branch == Cooker
%define release		%mkrel 2
%else
%define subrel		1
%define release		%mkrel 0
%endif

# Version of java
%define javaver		1.6.0

# Alternatives priority
%define priority	16000

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

Name:		icedtea-web
Version:	1.0.2
Release:	%{release}
Summary:	Additional Java components for OpenJDK
Group:		Networking/WWW
License:	LGPLv2+ and GPLv2 with exceptions
URL:		http://icedtea.classpath.org/wiki/IcedTea-Web
Source0:	http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz

BuildRequires:	desktop-file-utils
BuildRequires:	glib2-devel
BuildRequires:	gtk2-devel

# Need java-1.6.0-openjdk with IcedTea6 1.10 or newer
BuildRequires:	java-1.6.0-openjdk-devel >= 1.6.0.0-18.b22

BuildRequires:	xulrunner-devel
BuildRequires:	zip
BuildRequires:	zlib-devel

Requires:	java-1.6.0-openjdk
Requires(post):   update-alternatives
Requires(postun): update-alternatives

# Standard JPackage plugin provides.
Provides:	java-plugin = %{javaver}

Provides:	java-1.6.0-openjdk-plugin = 1.6.0.0-18.b22
Obsoletes:	java-1.6.0-openjdk-plugin

Patch0:		icedtea-web-1.0.2-mutex_and_leak.patch

%description
The IcedTea-Web project provides a Java web browser plugin, an implementation
of Java Web Start (originally based on the Netx project) and a settings tool to
manage deployment settings for the aforementioned plugin and Web Start
implementations. 

%package javadoc
Summary:    API documentation for IcedTea-Web
Group:      Documentation
Requires:   jpackage-utils
%if %mdkversion >= 201010
BuildArch:	noarch
%endif

%description javadoc
This package contains Javadocs for the IcedTea-Web project.

%prep
%setup -q
%patch0 -p1

%if %mdkversion < 201000
# ugly hack to make it work on 2009.0/mes5 (pcpa)
perl -pi -e 's|AC_CANONICAL_HOST||;' configure.*
autoreconf -fi
%endif

%build
%configure2_5x						\
	--with-pkgversion=mandriva-%{release}-%{_arch}	\
	--docdir=%{_javadocdir}/%{name}			\
	--prefix=%{jredir}/

make CXXFLAGS="%{optflags}"

%install
%makeinstall_std

# FIXME
rm -f %{buildroot}%{_prefix}/bin

# Remove pluginappletviewer ... it is unused and will be removed in 1.1
rm -f %{buildroot}%{jredir}/bin/pluginappletviewer

# Install desktop files.
install -d -m 755 %{buildroot}%{_datadir}/{applications,pixmaps}
cp javaws.png %{buildroot}%{_datadir}/pixmaps
desktop-file-install --vendor '' \
	--dir %{buildroot}%{_datadir}/applications javaws.desktop
desktop-file-install --vendor '' \
	--dir %{buildroot}%{_datadir}/applications itweb-settings.desktop

%posttrans
update-alternatives --remove %{javaplugin}				\
  %{javadir}/jre/lib/%{archinstall}/gcjwebplugin.so 2>/dev/null
update-alternatives --remove %{javaplugin}				\
  %{jredir}/lib/%{archinstall}/IcedTeaNPPlugin.so 2>/dev/null
update-alternatives							\
  --install %{_libdir}/mozilla/plugins/libjavaplugin.so %{javaplugin}	\
  %{jredir}/lib/%{archinstall}/IcedTeaPlugin.so %{priority}		\
  --slave %{_bindir}/javaws javaws %{jredir}/bin/javaws			\
  --slave %{_mandir}/man1/javaws.1 javaws.1				\
  %{jredir}/man/man1/javaws.1
exit 0

%postun
if [ $1 -eq 0 ]; then
    alternatives --remove %{javaplugin}					\
	%{jredir}/lib/%{archinstall}/IcedTeaPlugin.so
fi
exit 0

%files
%defattr(-,root,root,-)
%{jredir}/bin/*
%{jredir}/lib/*
%{jredir}/man/man1/*
%{_datadir}/pixmaps/javaws.png
%{_datadir}/applications/javaws.desktop
%{_datadir}/applications/itweb-settings.desktop
%doc %{_javadocdir}/%{name}
%doc NEWS README COPYING
