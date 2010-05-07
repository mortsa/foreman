%global homedir %{_datadir}/%{name}
%global confdir extras/spec

Name:           foreman
Version:        0.1.4
Release:        4%{?dist}
Summary:        Systems Management web application

Group:          Applications/System
License:        GPLv3+
URL:            http://theforeman.org
Source0:        http://github.com/ohadlevy/%{name}/tarball/%{name}-0.1-4.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

Requires:       ruby(abi) = 1.8
Requires:       rubygems
Requires:       rubygem(rack) >= 1.0.1
Requires:       rubygem(rake) >= 0.8.3
Requires:       puppet >= 0.24.4
Requires:       rubygem(sqlite3-ruby)
Requires(pre):  shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

Packager:       Ohad Levy <ohadlevy@gmail.com>

%description
Foreman is aimed to be a Single Address For All Machines Life Cycle Management.
Foreman is based on Ruby on Rails, and this package bundles Rails and all
plugins required for Foreman to work.

%prep
%setup -q -n %{name}

%build

%install
rm -rf %{buildroot}
install -d -m0755 %{buildroot}%{_datadir}/%{name}
install -d -m0755 %{buildroot}%{_sysconfdir}/%{name}
install -d -m0755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m0755 %{buildroot}%{_localstatedir}/run/%{name}
install -d -m0750 %{buildroot}%{_localstatedir}/log/%{name}

install -Dp -m0644 %{confdir}/%{name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -Dp -m0755 %{confdir}/%{name}.init %{buildroot}%{_initrddir}/%{name}
cp -p -r app config extras lib Rakefile script vendor %{buildroot}%{_datadir}/%{name}
chmod a+x %{buildroot}%{_datadir}/%{name}/script/{console,dbconsole,runner}
rm -rf %{buildroot}%{_datadir}/%{name}/extras/{jumpstart,spec}
rm -rf %{buildroot}%{_datadir}/%{name}/VERSION

# Move config files to %{_sysconfdir}
mv %{buildroot}%{_datadir}/%{name}/config/email.yaml.example %{buildroot}%{_datadir}/%{name}/config/email.yaml
for i in database.yml environment.rb email.yaml settings.yaml; do
    mv %{buildroot}%{_datadir}/%{name}/config/$i %{buildroot}%{_sysconfdir}/%{name}
    ln -sv %{_sysconfdir}/%{name}/$i %{buildroot}%{_datadir}/%{name}/config/$i
done

# Put db in %{_localstatedir}/lib/%{name}/db
cp -pr db/migrate %{buildroot}%{_datadir}/%{name}
mkdir %{buildroot}%{_localstatedir}/lib/%{name}/db
ln -sv %{_localstatedir}/lib/%{name}/db %{buildroot}%{_datadir}/%{name}/db
ln -sv %{_datadir}/%{name}/migrate %{buildroot}%{_localstatedir}/lib/%{name}/db/migrate

# Put HTML %{_localstatedir}/lib/%{name}/public
cp -pr public %{buildroot}%{_localstatedir}/lib/%{name}/
ln -sv %{_localstatedir}/lib/%{name}/public %{buildroot}%{_datadir}/%{name}/public

# Put logs in %{_localstatedir}/log/%{name}
ln -sv %{_localstatedir}/log/%{name} %{buildroot}%{_datadir}/%{name}/log

# Put tmp files in %{_localstatedir}/run/%{name}
ln -sv %{_localstatedir}/run/%{name} %{buildroot}%{_datadir}/%{name}/tmp

# Create a script for migrating the database
cat << \EOF > %{buildroot}%{_datadir}/%{name}/extras/dbmigrate
#!/bin/sh
cd && /usr/bin/rake db:migrate RAILS_ENV=production
EOF
chmod a+x %{buildroot}%{_datadir}/%{name}/extras/dbmigrate

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc README
%{_datadir}/%{name}
%{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(-,%{name},%{name}) %{_localstatedir}/lib/%{name}
%attr(-,%{name},%{name}) %{_localstatedir}/log/%{name}
%attr(-,%{name},%{name}) %{_localstatedir}/run/%{name}

%pre
# Add the "foreman" user and group
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -G puppet -d %{homedir} -s /sbin/nologin -c "Foreman" %{name}
exit 0

%post
/sbin/chkconfig --add %{name} || ::

# initialize/migrate the database (defaults to SQLITE3)
su - foreman -s /bin/bash -c %{_datadir}/%{name}/extras/dbmigrate >/dev/null 2>&1 || :

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name} || :
fi

%postun
if [ $1 -ge 1 ] ; then
    # Restart the service
    /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%changelog
* Fri Apr 30 2010 Todd Zullinger <tmz@pobox.com> - 0.1.4-4
- Rework %%install for better FHS compliance
- Misc. adjustments to match Fedora/EPEL packaging guidelines
- Update License field to GPLv3+ to match README
- Use foreman as the primary group for the foreman user instead of puppet
- This breaks compatibility with previous RPM, as directories can't be replaced with links easily.

* Thu Apr 19 2010 Ohad Levy <ohadlevy@gmail.com> - 0.1-4-3
- added status to startup script
- removed puppet module from the RPM

* Thu Apr 12 2010 Ohad Levy <ohadlevy@gmail.com> - 0.1.4-2
- Added startup script for built in webrick server
- Changed foreman user default shell to /sbin/nologin and is now part of the puppet group
- defaults to sqlite database

* Thu Apr 6 2010 Ohad Levy <ohadlevy@gmail.com> - 0.1.4-1
- Initial release.