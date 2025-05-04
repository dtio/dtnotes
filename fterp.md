cd to PVC
mkdir backup
cp backupfiles to backupdirectory

cd frappe-bench/sites
bench --site en.fosstech.biz restore backup/db.tgz --with-public-files backup/publicfile.tar --with-private-files backup/privatefile.tar --force
bench --site en.fosstech.biz migrate

===============

bench --site en.fosstech.biz backup --with-files