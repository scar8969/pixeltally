-- 📊 analytics schema
CREATE TABLE sites(id INTEGER PRIMARY KEY, domain TEXT UNIQUE, created_at DATETIME);
CREATE TABLE page_views(id INTEGER PRIMARY KEY, site_id INTEGER REFERENCES sites(id), path TEXT DEFAULT '/', referrer TEXT, ip_hash TEXT, ua TEXT, country TEXT, at DATETIME);
CREATE TABLE daily_aggs(id INTEGER PRIMARY KEY, site_id INTEGER REFERENCES sites(id), date TEXT, views INTEGER DEFAULT 0, visitors INTEGER DEFAULT 0);
