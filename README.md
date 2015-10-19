# Analytical-Pricing-Solution

Analytical-Pricing-Solution Wiki Ref :

https://github.com/ptoraskar/analytical-pricing-solution/wiki

Following library are necessary for Pandas, Scipy and seaborn:

 1. libblas-dev
 2. liblapack-dev
 3. libpng-dev
 4. libjpeg8-dev
 5. libfreetype8-dev
 6. libatlas-base
 7. gfortran


Installation PostgreSQL :

Install dependencies for PostgreSQL

	sudo apt-get install libpq-dev python-dev

Install PostgreSQL
	
	sudo apt-get install postgresql postgresql-contrib

Configure PostgreSQL

	1. Start off by running
		sudo su - postgres
	2. Create your database
		createdb apsdb
	3. Create your database user 
		createuser -P apsuser (password : <aps_pg>)
	4. Activate the PostgreSQL command line interface like so
		psql
	5. Grant this new user access to your new database
		$ postgres=# GRANT ALL PRIVILEGES ON DATABASE apsdb TO apsuser;
		  GRANT
	6. Exit

Install a backend for PostgreSQL:

	pip install psycopg2


