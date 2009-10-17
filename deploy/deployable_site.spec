%define name example_project
%define version 1.2
%define release 1
%define __prelink_undo_cmd %{nil}

Summary: Example_Project website
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Source1: Django-1.1.tar.gz
Source2: south-0.6.tar.gz
Source3: html5lib-0.11.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: x86_64
Vendor: Chris Adams <chris@improbable.org>
Requires: python26, python26-imaging, python26-virtualenv, python26-psycopg2
BuildRequires: tar, python26-virtualenv, python26-pip, python26-setuptools
Url: http://www.example.org
License: BSD
Group: MostAppropriateGroup

%description
Bundled virtualenv for the example_project website

%prep

if [ -d $RPM_BUILD_ROOT/usr/local/example_project-env ]; then
    echo "Cleaning out stale build directory" 1>&2
    rm -rf $RPM_BUILD_ROOT/usr/local/example_project-env
fi

%install

mkdir -p $RPM_BUILD_ROOT/usr/local/example_project-env

virtualenv-2.6 $RPM_BUILD_ROOT/usr/local/example_project-env

# Install our libraries:
$RPM_BUILD_ROOT/usr/local/example_project-env/bin/easy_install-2.6 %{SOURCE1}
$RPM_BUILD_ROOT/usr/local/example_project-env/bin/easy_install-2.6 %{SOURCE2}
$RPM_BUILD_ROOT/usr/local/example_project-env/bin/easy_install-2.6 %{SOURCE3}

# Unpack the example_project tarball:
tar -C $RPM_BUILD_ROOT/usr/local/example_project-env -xzf %{SOURCE0}
mv $RPM_BUILD_ROOT/usr/local/example_project-env/example_project-%{version} $RPM_BUILD_ROOT/usr/local/example_project-env/example_project

# Unpack sb_auth, which is not currently setup.py enabled:
tar -C $RPM_BUILD_ROOT/usr/local/example_project-env/example_project/apps -xzf %{SOURCE4}

# Convenience for working in the virtualenv:
mv $RPM_BUILD_ROOT/usr/local/example_project-env/example_project/virtualenv-postactivate.sh $RPM_BUILD_ROOT/usr/local/example_project-env/bin/postactivate
perl -p -i -e 's|$HOME/Projects|/usr/local/example_project-env|g' $RPM_BUILD_ROOT/usr/local/example_project-env/bin/postactivate

# Correct the virtualenv lib64 symlink for what it will point to on a real install:

rm $RPM_BUILD_ROOT/usr/local/example_project-env/lib64

ln -s /usr/local/example_project-env/lib $RPM_BUILD_ROOT/usr/local/example_project-env/lib64

find $RPM_BUILD_ROOT -name \*.py[co] -delete

# Clean up many hard-coded paths:
virtualenv-2.6 --relocatable $RPM_BUILD_ROOT/usr/local/example_project-env

# The above doesn't actually work reliably, so we'll kludge it:
grep -lrZF "#!$RPM_BUILD_ROOT" $RPM_BUILD_ROOT | xargs -r -0 perl -p -i -e "s|$RPM_BUILD_ROOT||g"

perl -p -i -e "s|$RPM_BUILD_ROOT||g" $RPM_BUILD_ROOT/usr/local/example_project-env/bin/activate

perl -p -i -e "s|PROJECT_ROOT=.*|PROJECT_ROOT=/usr/local/example_project-env/example_project|g" $RPM_BUILD_ROOT/usr/local/example_project-env/bin/postactivate

echo ". /usr/local/example_project-env/bin/postactivate" >> $RPM_BUILD_ROOT/usr/local/example_project-env/bin/activate

# This avoids prelink & RPM helpfully breaking the package signatures:
prelink -u $RPM_BUILD_ROOT/usr/local/example_project-env/bin/python
prelink -u $RPM_BUILD_ROOT/usr/local/example_project-env/bin/python26

# Fix Django paths - this avoids having our Apache config hard-code the .egg path:
ln -s /usr/local/example_project-env/lib/python2.6/site-packages/Django-1.1-py2.6.egg/django $RPM_BUILD_ROOT/usr/local/example_project-env/lib/python2.6/site-packages/django

%post

# Create the directories which will contain user-uploaded media:
install -d -o root -g apache -m 775 /usr/local/example_project-env/example_project/site_media/uploads

# Pre-compile all of our Python modules:
/usr/local/example_project-env/bin/python26 -m compileall -q /usr/local/example_project-env

chgrp apache /usr/local/example_project-env/example_project/local_settings.py /usr/local/example_project-env/example_project/local_settings.pyc
chmod g+rw,o-rwx /usr/local/example_project-env/example_project/local_settings.py /usr/local/example_project-env/example_project/local_settings.pyc

%clean
rm -rf $RPM_BUILD_ROOT

%files
/
%defattr(-,root,root)
