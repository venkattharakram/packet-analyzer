CREATE ROLE packetuser WITH LOGIN PASSWORD 'packetpass';
CREATE DATABASE packetdb OWNER packetuser;
GRANT ALL PRIVILEGES ON DATABASE packetdb TO packetuser;

