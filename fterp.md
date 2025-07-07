cd to PVC
mkdir backup
cp backupfiles to backupdirectory

kubectl cp backup/20250602_153836-en_fosstech_biz-private-files.tar erpnext/frappe-bench-erpnext-worker-l-9dc464b68-pb7xg:/home/frappe/frappe-bench/sites/backup

cd frappe-bench/sites

bench --site en.fosstech.biz restore backup/db.tgz --with-public-files backup/publicfile.tar --with-private-files backup/privatefile.tar --force

Password: changeit

bench --site en.fosstech.biz migrate

===============

bench --site en.fosstech.biz backup --with-files