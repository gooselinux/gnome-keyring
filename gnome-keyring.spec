%define glib2_version 2.16.0
%define gtk2_version 2.6.0
%define dbus_version 1.0
%define hal_version 0.5.7
%define gcrypt_version 1.2.2
%define libtasn1_version 0.3.4

Summary: Framework for managing passwords and other secrets
Name: gnome-keyring
Version: 2.28.2
Release: 6%{?dist}
License: GPLv2+ and LGPLv2+
Group: System Environment/Libraries
Source: http://download.gnome.org/sources/gnome-keyring/2.28/gnome-keyring-%{version}.tar.bz2

# https://bugzilla.gnome.org/show_bug.cgi?id=598494
Patch2: gnome-keyring-2.28.0-die-on-session-exit.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=613644
Patch3: gnome-keyring-dir-prefix.patch

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=589203
Patch4: gnome-keyring-translations.patch
Patch5: gnome-keyring-translations-2.patch

URL: http://www.gnome.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: GConf2-devel
BuildRequires: dbus-devel >= %{dbus_version}
BuildRequires: libgcrypt-devel >= %{gcrypt_version}
BuildRequires: libtasn1-devel >= %{libtasn1_version}
BuildRequires: pam-devel
BuildRequires: libtool
BuildRequires: gettext
BuildRequires: intltool
BuildRequires: libtasn1-tools
Requires(pre): GConf2
Requires(preun): GConf2
Requires(post): GConf2

%description
The gnome-keyring session daemon manages passwords and other types of
secrets for the user, storing them encrypted with a main password.
Applications can use the gnome-keyring library to integrate with the keyring.

%package devel
Summary: Development files for gnome-keyring
License: LGPLv2+
Group: Development/Libraries
Requires: %name = %{version}-%{release}
Requires: glib2-devel
Requires: pkgconfig
# for /usr/share/gtk-doc/html
Requires: gtk-doc

%description devel
The gnome-keyring-devel package contains the libraries and
header files needed to develop applications that use gnome-keyring.

%package pam
Summary: Pam module for unlocking keyrings
License: LGPLv2+
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
# for /lib/security
Requires: pam

%description pam
The gnome-keyring-pam package contains a pam module that can
automatically unlock the "login" keyring when the user logs in.


%prep
%setup -q -n gnome-keyring-%{version}
%patch2 -p1 -b .die-on-session-exit
%patch3 -p1 -b .dir-prefix
%patch4 -p1 -b .translations
%patch5 -p2 -b .translations2

%build
%configure --disable-gtk-doc --with-pam-dir=/%{_lib}/security --disable-acl-prompts
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

# avoid unneeded direct dependencies
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' libtool

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install install-pam DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

rm $RPM_BUILD_ROOT/%{_lib}/security/*.la
rm $RPM_BUILD_ROOT%{_libdir}/*.la
rm $RPM_BUILD_ROOT%{_libdir}/gnome-keyring/*.la
rm $RPM_BUILD_ROOT%{_libdir}/gnome-keyring/devel/*.la
rm $RPM_BUILD_ROOT%{_libdir}/gnome-keyring/standalone/*.la

%find_lang gnome-keyring

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/gnome-keyring.schemas > /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gnome-keyring.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gnome-keyring.schemas > /dev/null || :
fi

%postun -p /sbin/ldconfig

%files -f gnome-keyring.lang
%defattr(-, root, root)
%doc AUTHORS NEWS README COPYING COPYING.LIB
# LGPL
%{_libdir}/lib*.so.*
%dir %{_libdir}/gnome-keyring
%{_libdir}/gnome-keyring/gnome-keyring-pkcs11.so
%{_libdir}/gnome-keyring/devel/*.so
%{_libdir}/gnome-keyring/standalone/*.so
# GPL
%{_bindir}/*
%{_libexecdir}/*
%{_datadir}/dbus-1/services/org.gnome.keyring.service
%{_datadir}/gcr
%{_sysconfdir}/gconf/schemas/gnome-keyring.schemas
%{_sysconfdir}/xdg/autostart/gnome-keyring-daemon.desktop

%files devel
%defattr(-, root, root)
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%doc %{_datadir}/gtk-doc/html/gnome-keyring/
%doc %{_datadir}/gtk-doc/html/gp11/
%doc %{_datadir}/gtk-doc/html/gcr/

%files pam
%defattr(-, root, root)
/%{_lib}/security/*.so

%changelog
* Wed Jul 28 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.28.2-6
- Additional translations (#589203)

* Mon May 10 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-5
- Updated translations
Resolves: #589203

* Fri Mar 26 2010 Ray Strode <rstrode@redhat.com> 2.28.2-4
- One more relocation fix
  Resolves: #575943

* Mon Mar 22 2010 Ray Strode <rstrode@redhat.com> 2.28.2-3
Resolves: #575943
- Support relocatable .gnome2

* Mon Jan 11 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.28.2-2
- Spec file cleanup, fix rpaths

* Mon Dec 14 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.28.2-1
- Update to 2.28.2

* Mon Oct 19 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.28.1-1
- Update to 2.28.1

* Wed Oct 14 2009 Ray Strode <rstrode@redhat.com> - 2.28.0-4
- Die on ctrl-alt-backspace and other abrupt exits

* Thu Oct  8 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-3
- Fix handling of rsa1 keys

* Fri Oct  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Avoid a 10 second delay at logout

* Mon Sep 21 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Mon Sep 14 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Tue Aug 11 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.90-1
- Update to 2.27.90

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Thu Jul  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-2
- Rebuild

* Sun Apr 12 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gnome-keyring/2.26/gnome-keyring-2.26.1.news

* Wed Apr  8 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-4
- Fix service activation

* Tue Apr  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-3
- Revert the previous patch since it causes crashes

* Thu Apr 02 2009 Richard Hughes  <rhughes@redhat.com> - 2.26.0-2
- Fix a nasty bug that's been fixed upstream where gnome-keyring-daemon
  would hang when re-allocating from a pool of secure memory.

* Mon Mar 16 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Feb 14 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.90-4
- Update to 2.25.90

* Tue Jan 20 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Thu Jan  8 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.4.2-1
- Update to 2.25.4.2

* Tue Jan  6 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.4.1-1
- Update to 2.25.4.1

* Mon Jan  5 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.4-1
- Update to 2.25.4

* Sat Dec 20 2008 Ray Strode <rstrode@redhat.com> - 2.25.2-3
- Init dbus later (fixes ssh-agent,
  patch from Yanko Kaneti, bug 476300)

* Fri Dec 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.2-2
- Update to 2.25.2

* Sun Nov 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.1-2
- Tweak description

* Mon Nov 10 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.25.1-1
- Update to 2.25.1

* Sun Oct 19 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Sun Sep 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-2
- Update to 2.24.0

* Sun Sep  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Thu Sep  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Wed Aug 20 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Mon Aug 11 2008 Colin Walters <walters@redhat.com> - 2.22.3.6-2
- Add --disable-acl-prompts; you can't try to maintain integrity
  between two processes with the same UID and no other form of
  access control.

* Mon Aug  4 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Thu May 29 2008 Colin Walters <walters@redhat.com> - 2.22.2-2
- Add patch to nuke allow-deny dialog, see linked upstream bug
  for discussion

* Tue May 27 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.22.2-1
- Update to 2.22.2

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Sun Feb 24 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Tue Feb 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91
- Drop upstreamed patch

* Wed Feb  6 2008 Ray Strode <rstrode@redhat.com> - 2.21.90-2
- Fix problem in patch for bug 430525

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Mon Jan 28 2008 Ray Strode <rstrode@redhat.com> - 2.21.5-3
- Don't ask for a password...ever (bug 430525)

* Mon Jan 21 2008 Matthew Barnes  <mbarnes@redhat.com> - 2.21.5-2
- Fix a race condition that was causing Evolution to hang (#429097)

* Mon Jan 14 2008 Matthias Clasen  <mclasen@redhat.com> - 2.21.5-1
- Update to 2.21.5

* Tue Dec 18 2007 Matthias Clasen  <mclasen@redhat.com> - 2.21.4-1
- Update to 2.21.4

* Fri Dec  7 2007 Matthias Clasen  <mclasen@redhat.com> - 2.21.3.2-1
- Update to 2.21.3.2

* Fri Nov 30 2007 Matthias Clasen  <mclasen@redhat.com> - 2.20.2-2
- Reenable auto-unlock

* Mon Nov 26 2007 Matthias Clasen  <mclasen@redhat.com> - 2.20.2-1
- Update to 2.20.2

* Sun Nov 11 2007 Matthias Clasen  <mclasen@redhat.com> - 2.20.1-4
- Don't ship a .la file (#370531)

* Thu Oct 25 2007 Christopher Aillon <caillon@redhat.com> - 2.20.1-3
- Rebuild

* Mon Oct 15 2007 Matthias Clasen  <mclasen@redhat.com> - 2.20.1-2
- Disable the auto-unlock question for now (#312531)

* Mon Oct 15 2007 Matthias Clasen  <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1
- Drop obsolete patches
- Add bug ref for selinux patch

* Tue Oct  9 2007 Matthias Clasen  <mclasen@redhat.com> - 2.20-6
- Avoid undefined symbols in the pam module

* Mon Oct  8 2007 Alexander Larsson <alexl@redhat.com> - 2.20-5
- Fixed minor issue with pam-selinux issue pointed out by stef

* Thu Oct  4 2007 Alexander Larsson <alexl@redhat.com> - 2.20-4
- Have the pam module tell the daemon to init the login keyring 
  without using the socket as selinux limits access to that

* Thu Oct  4 2007 Alexander Larsson <alexl@redhat.com> - 2.20-3
- Add NO_MATCH error patch from svn. Will fix apps that
  can't handle empty list matches

* Mon Oct 3 2007 Alexander Larsson <alexl@redhat.com> - 2.20-2
- Backport fix from svn where newly created keyrings weren't
  found
- Don't unset default keyring on daemon shutdown

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20-1
- Update to 2.20

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.91-1
- Update to 2.19.91

* Sun Aug 12 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.90-1
- Update to 2.19.90

* Thu Aug  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6.1-2
- Update License fields

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6.1-1
- Update to 2.19.6.1

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-2
- Backport a fix from upstream

* Fri Jul 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-1
- Update to 2.19.6
- Add a pam subpackage

* Mon Jul  9 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Sun May 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 0.8-1
- Update to 0.8

* Sat Feb 24 2007 Matthias Clasen <mclasen@redhat.com> - 0.7.92-1
- Update to 0.7.92

* Mon Feb 12 2007 Matthias Clasen <mclasen@redhat.com> - 0.7.91-1
- Update to 0.7.91

* Thu Feb  8 2007 Matthias Clasen <mclasen@redhat.com> - 0.7.3-2
- Package review cleanup

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 0.7.3-1
- Update to 0.7.3

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 0.7.2-1
- Update to 0.7.2

* Mon Nov  6 2006 Matthias Clasen <mclasen@redhat.com> - 0.7.1-1
- Update to 0.7.1

* Mon Sep  4 2006 Alexander Larsson <alexl@redhat.com> - 0.6.0-1
- update to 0.6.0

* Wed Aug 23 2006 Dan Williams <dcbw@redhat.com> - 0.5.2-2.fc6
- Fix null pointer dereference (Gnome.org #352587)

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.2-1.fc6
- Update to 0.5.2

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.5.1-1.1
- rebuild

* Tue Jun 13 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.1-1
- Update to 0.5.1

* Mon May 29 2006 Alexander Larsson <alexl@redhat.com> - 0.4.9-2
- buildrequire gettext (#193377)

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 0.4.9-1
- Update to 0.4.9

* Mon Feb 27 2006 Matthias Clasen <mclasen@redhat.com> - 0.4.8-1
- Update to 0.4.8

* Mon Feb 13 2006 Matthias Clasen <mclasen@redhat.com> - 0.4.7-1
- Update to 0.4.7

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.4.6-1.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.4.6-1.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 30 2005 Matthias Clasen <mclasen@redhat.com> 0.4.6-1
- Update to 0.4.6

* Thu Sep 29 2005 Matthias Clasen <mclasen@redhat.com> 0.4.5-1
- Update to 0.4.5

* Wed Sep  7 2005 Matthias Clasen <mclasen@redhat.com> 0.4.4-1
- Update to 0.4.4

* Tue Aug 16 2005 David Zeuthen <davidz@redhat.com> 0.4.3-2
- Rebuilt

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> 0.4.3-1
- New upstream version

* Fri Mar 18 2005 David Zeuthen <davidz@redhat.com> 0.4.2-1
- New upstream version

* Wed Mar  2 2005 Alex Larsson <alexl@redhat.com> 0.4.1-2
- Rebuild

* Tue Feb  1 2005 Matthias Clasen <mclasen@redhat.com> - 0.4.1-1
- Update to 0.4.1

* Mon Sep 13 2004 Alexander Larsson <alexl@redhat.com> - 0.4.0-1
- update to 0.4.0

* Tue Aug 31 2004 Alex Larsson <alexl@redhat.com> 0.3.3-1
- update to 0.3.3

* Thu Aug 12 2004 Alexander Larsson <alexl@redhat.com> - 0.3.2-1
- update to 0.3.2

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Apr  1 2004 Alex Larsson <alexl@redhat.com> 0.2.0-1
- update to 0.2.0

* Wed Mar 10 2004 Alexander Larsson <alexl@redhat.com> 0.1.90-1
- update to 0.1.90

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 24 2004 Alexander Larsson <alexl@redhat.com> 0.1.4-1
- update to 0.1.4

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jan 30 2004 Alexander Larsson <alexl@redhat.com> 0.1.3-1
- update to 0.1.3

* Mon Jan 26 2004 Bill Nottingham <notting@redhat.com>
- tweak summary

* Mon Jan 26 2004 Alexander Larsson <alexl@redhat.com> 0.1.2-2
- devel package only needs glib2-devel, not gtk2-devel

* Fri Jan 23 2004 Alexander Larsson <alexl@redhat.com> 0.1.2-1
- First version
