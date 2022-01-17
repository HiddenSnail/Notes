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
%define _tool_chain_path /home/dapp/compiler/gcc-linaro-10.2.1-2021.02-x86_64_aarch64-linux-gnu/bin
#不生成debug包，避免生成debug包时会出现错误
%define debug_package    %{nil}

%prep

%setup -q
pwd
export PATH=%{_tool_chain_path}:$PATH
#交叉编译./auto/cc/name文件中的ngx_feature_run开关需要关掉
sed -i "s/ngx_feature_run=.*/ngx_feature_run=no/g" ./auto/cc/name
#交叉编译./auto/types/sizeof的ngx_size需要手动定义
sed -i "s/ngx_size=.*/ngx_size=4/g" ./auto/types/sizeof 
#交叉编译指定PCRE的编译器
sed -i "s/PCRE_CONF_OPT=[\n|\r|.]*/PCRE_CONF_OPT=--host=aarch64-linux-gnu/g" ./auto/options
#交叉编译场景下,通过Nginx触发OpenSSL需要调用OpenSSL的Confiure程序,而不是config.原因是config程序生成的MakeFile是以当前平台做为目标平台生成的，Configure可以手动配置目标平台是以当前平台做为目标平台生成的，Configure可以手动配置目标平台
sed -i "s/config/Configure/g" ./auto/lib/openssl/make

%build
./configure \
	--with-cc=aarch64-linux-gnu-gcc \
	--with-cpp=aarch64-linux-gnu-g++ \
	--with-cc-opt="-Wno-error -DNGX_SYS_NERR=132 -DNGX_HAVE_GCC_ATOMIC=1 -DNGX_HAVE_SYSVSHM=1" \
	--with-ld-opt="-Wl,--dynamic-linker=../lib/ld-linux-aarch64.so.1,--rpath=../lib -lpthread" \
	--prefix=%{_prefix} \
	--with-http_ssl_module \
	--with-http_flv_module \
	--with-openssl=/mdw/openssl-OpenSSL_1_1_0i \
	#此处设置了OpenSSL的Configure程序的目标平台和交叉编译器类型
	--with-openssl-opt="linux-aarch64 --cross-compile-prefix=aarch64-linux-gnu-" \
	--with-pcre=/mdw/pcre-8.40 \
	--with-zlib=/mdw/zlib-1.2.11 \
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
                         
