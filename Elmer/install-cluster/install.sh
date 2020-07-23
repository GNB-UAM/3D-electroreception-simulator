wget https://github.com/cTatu/tfgflama/raw/master/Elmer/install-cluster/build-20200629-2.x86_64.rpm

rpm2cpio build-20200629-2.x86_64.rpm | cpio -idv

mv usr/local/* usr/
rm -r usr/local

wget http://mirror.centos.org/centos/6/os/x86_64/Packages/blas-3.2.1-5.el6.x86_64.rpm
wget http://mirror.centos.org/centos/6/os/x86_64/Packages/lapack-3.2.1-5.el6.x86_64.rpm
wget http://mirror.centos.org/centos/7/os/x86_64/Packages/libgfortran-4.8.5-39.el7.x86_64.rpm
wget http://mirror.centos.org/centos/6/os/x86_64/Packages/libquadmath-7.2.1-1.2.1.el6.x86_64.rpm
wget http://mirror.centos.org/centos/7/os/x86_64/Packages/glibc-2.17-307.el7.1.x86_64.rpm

for i in *.rpm; do
    rpm2cpio "$i" | cpio -idv
done

rm *.rpm

export ELMER_HOME=/home/asp04/usr/

LD_LIBRARY_PATH=/home/asp04/lib64/:/home/asp04/usr/lib64/:$LD_LIBRARY_PATH lib64/ld-2.17.so usr/bin/ElmerSolver --version
