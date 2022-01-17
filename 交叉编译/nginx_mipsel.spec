Name: nginx
Version: 1.12.2
Release:        1%{?dist}
Summary:nginx rmp package production

Group:  Applications/Archiving
License:GPLv2
URL:    https://github.com/ddcw/nginx
Source0:%{name}-%{version}.tar.gz
Source1:lib.tar.gz

#BuildRequires:

%description
this is for install nginx

%define	_prefix        	 /opt/nginx
%define _tool_chain_path /home/dapp/compiler/mips-loongson-gcc8-linux-gnu-2021-02-08/bin
%define debug_package    %{nil}

%prep

%setup -q
pwd
export PATH=%{_tool_chain_path}:$PATH
sed -i "s/ngx_feature_run=.*/ngx_feature_run=no/g" ./auto/cc/name
sed -i "s/ngx_size=.*/ngx_size=4/g" ./auto/types/sizeof 
sed -i "s/PCRE_CONF_OPT=[\n|\r|.]*/PCRE_CONF_OPT=--host=mips-linux-gnu/g" ./auto/options
sed -i "s/config/Configure/g" ./auto/lib/openssl/make

%build
./configure \
	--with-cc=mips-linux-gnu-gcc \
	--with-cpp=mips-linux-gnu-g++ \
	--with-cc-opt="-Wno-error -mips64r2 -mabi=64 -DNGX_SYS_NERR=132 -DNGX_HAVE_GCC_ATOMIC=1 -DNGX_HAVE_SYSVSHM=1" \
	--with-ld-opt="-mips64r2 -mabi=64 -Wl,--dynamic-linker=../lib/ld.so.1,--rpath=../lib,-lpthread" \
	--prefix=%{_prefix} \
	--with-http_ssl_module \
	--with-http_flv_module \
	--with-openssl=/mdw/openssl-OpenSSL_1_1_0i \
	--with-openssl-opt="linux64-mips64 --cross-compile-prefix=mips-linux-gnu- -mips64r2 -mabi=64" \
	--with-pcre=/mdw/pcre-8.40 \
	--with-pcre-opt="-mips64r2 -mabi=64" \
	--with-zlib=/mdw/zlib-1.2.11 \
	--with-zlib-opt="-mips64r2 -mabi=64" \
	--with-http_stub_status_module \
	--with-http_sub_module \
	--with-http_realip_module \
	--with-stream_realip_module \
	--with-stream \
	--with-http_gunzip_module \
	--with-http_auth_request_module
	
make

%install
make install DESTDIR=%{buildroot} && tar -xvf %{SOURCE1} -C %{buildroot}%{_prefix}
chmod 755 -R %{buildroot}%{_prefix}/lib

%files
/opt/nginx
%doc



%changelog
                         
