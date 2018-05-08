
SELECT full_visitor_id,
  geonetwork_country,
  geonetwork_region,
  geonetwork_city,
  hits_page_hostname,
  hits_page_pagetitle,
  vertical,
  device_mobiledevicebranding,
  device_mobiledevicemodel,
  device_language,
  hits_referer,
  hits_page_pagepath,
  avg(hits_hour::INT) hits_hour,
  COUNT(DISTINCT event_id) event_count, 
  sum ( CASE WHEN hit_type = 'PAGE' then 1 ELSE NULL END) AS page_hits,
  sum ( CASE WHEN hit_type = 'EVENT' then 1 ELSE NULL END) AS event_hits,
  avg (totals_bounces) as bounces,
  AVG (totals_hits) AS hits,
  avg(totals_newvisits) AS newvisits,
  AVG(totals_pageviews) as pageviews,
  AVG(totals_screenviews) as screenviews, 
  AVG(totals_timeonscreen) as timeonscreen,
  AVG(totals_timeonsite) as timeonsite,
  AVG(totals_bounces) as bounces,
  AVG(totals_newvisits) newvisits,
  COUNT(trafficsource_istruedirect) direct_traffic_count,
  hits_eventinfo_eventcategory,
  AVG(CASE WHEN device_browser = 'Chrome' THEN 1 ELSE 0 END) AS browser_count_chrome,
  AVG(CASE WHEN device_operatingsystem = 'Chrome' THEN 1 ELSE 0 END) AS os_count_windows,
  AVG(CASE WHEN device_operatingsystem = 'Windows' THEN 1 ELSE 0 END) AS os_count_windows,
  AVG(CASE WHEN device_operatingsystem = 'iOS' THEN 1 ELSE 0 END) AS os_count_ios,
  AVG(CASE WHEN device_operatingsystem = 'Android' THEN 1 ELSE 0 END) AS os_count_android,
  AVG(CASE WHEN device_operatingsystem = 'Macintosh' THEN 1 ELSE 0 END) AS os_count_mac,
  AVG(CASE WHEN device_operatingsystem = 'Linux' THEN 1 ELSE 0 END) AS os_count_linux,
  AVG(CASE WHEN device_operatingsystem = 'Chrome OS' THEN 1 ELSE 0 END) AS os_count_chrome,
  AVG(case when lower(hits_isinteraction) = 'true' then 1 else 0 END) interaction_count,
  AVG(case when hits_isentrance = 'true' then 1 else 0 END) entrance_count,
  AVG(case when hits_isexit = 'true' then 1 else 0 END) exit_count,
  sum(case when hits_eventinfo_eventcategory = 'ArticlePage' then 1 else 0 END) as article_page_count,
  sum(case when hits_eventinfo_eventcategory = 'ArticleShareFixedModule' then 1 else 0 END) as article_share_count,
  sum(case when hits_eventinfo_eventcategory = 'ArticleUpNext' then 1 else 0 END) as article_next_count,
  sum(case when hits_eventinfo_eventcategory = 'CookieImplicitConsentBanner' then 1 else 0 END) as article_cookie_consent_count,
  sum(case when hits_eventinfo_eventcategory = 'ArticleRelatedVideoModule' then 1 else 0 END) as article_related_video_count,
  sum(case when hits_eventinfo_eventaction = 'View' then 1 else 0 END) view_action_count,
  sum(case when hits_eventinfo_eventaction = 'ScrollDepth' then 1 else 0 END) as scroll_depth_count,
  sum(case when hits_eventinfo_eventaction = 'ScrolledTo' then 1 else 0 END) as scroll_to_count,
  sum(case when hits_eventinfo_eventaction = 'ScrollDepth_articlePreview' then 1 else 0 END) article_preview_count,
  avg(case when hits_eventinfo_eventlabel = '50_0' then 1 else 0 END) as scroll_50_count,
  sum(case when hits_eventinfo_eventlabel = '75_0' then 1 else 0 END) as scroll_75_count,
  sum(case when hits_eventinfo_eventlabel = '100_0' then 1 else 0 END) as scroll_100_count
FROM gaa.mw_events_daily_tmp
--WHERE hits_eventinfo_eventcategory = 'ArticlePage'
GROUP BY full_visitor_id,
  geonetwork_country,
  geonetwork_region,
  geonetwork_city,
  hits_page_hostname,
  hits_page_pagetitle,
  vertical,
  device_mobiledevicebranding,
  device_mobiledevicemodel,
  device_language,
  hits_referer,
  hits_page_pagepath,
  hits_eventinfo_eventcategory
  -- hit_number is just a sequence id to signify if hit is 1st, 2nd, etc
limit 50;

SELECT  AVG(totals_hits) over ( order by DATE_TRUNC('day', visit_date::DATE) rows between 2 preceding and current row) weekly_hits
from gaa.mw_events_daily_tmp
where full_visitor_id = '3421930274517514191'
group by visit_date, totals_hits;

UNLOAD
(
	$$
	SELECT 
	  trafficsource_referralpath,
	  trafficsource_campaign,
	  trafficsource_source,
	  trafficsource_medium,
	  device_browser,
	  device_operatingsystemversion,
	  device_mobiledevicemodel,
	  geonetwork_country,
	  geonetwork_region,
	  geonetwork_metro,
	  geonetwork_city,
	  hits_page_pagepath,
	  hits_page_pagetitle,
	  hits_appinfo_appname,
	  hits_appinfo_appversion,
	  hits_appinfo_screenname,
	  AVG(COALESCE(totals_screenviews, 0)) screen_views,
	  AVG(COALESCE(totals_pageviews, 0)) page_views,
--	  COALESCE(max(COALESCE(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT)), 0) article_consumption_level
      CASE max(COALESCE(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT)) 
		  WHEN 50 THEN 0
		  WHEN 75 THEN 1
		  ELSE  2
	  END  article_consumption_level
	--  CASE max(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT)
	--  	WHEN 75 THEN 1 
	--  ELSE 0 END AS scroll_75,
	--  CASE max(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT) 
	--  	WHEN 50 THEN 1 
	--  ELSE 0 END AS scroll_50
	FROM gaa.mw_events_201803 
	where hits_eventinfo_eventcategory = 'ArticlePage'  
	group by 
	  trafficsource_referralpath,
	  trafficsource_campaign,
	  trafficsource_medium,
	  trafficsource_source,
	  device_browser,
	  device_browserversion,
	  device_operatingsystem,
	  device_operatingsystemversion,
	  device_devicecategory,
	  device_mobiledevicemodel,
	  geonetwork_country,
	  geonetwork_region,
	  geonetwork_metro,
	  geonetwork_city,
	  hits_page_pagepath,
	  hits_page_pagetitle,
	  hits_appinfo_appname,
	  hits_appinfo_appversion,
	  hits_appinfo_screenname,
	  hits_eventinfo_eventcategory
$$
)
TO 's3://vice-bi-vdw-dev/elias/scroll_traffic_'
DELIMITER '||'
CREDENTIALS 'aws_iam_role=arn:aws:iam::408275269683:role/bia-core-rst';

SELECT 
	  trafficsource_referralpath,
	  trafficsource_campaign,
	  trafficsource_source,
	  trafficsource_medium,
	  device_browser,
	  device_operatingsystemversion,
	  device_mobiledevicemodel,
	  geonetwork_country,
	  geonetwork_region,
	  geonetwork_metro,
	  geonetwork_city,
	  hits_page_pagepath,
	  hits_page_pagetitle,
	  hits_appinfo_appname,
	  hits_appinfo_appversion,
	  hits_appinfo_screenname,
	  AVG(COALESCE(totals_screenviews, 0)) screen_views,
	  AVG(COALESCE(totals_pageviews, 0)) page_views,
--	  COALESCE(max(COALESCE(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT)), 0) article_consumption_level
	  CASE max(COALESCE(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT)) 
	  	WHEN 50 THEN 0
	  	WHEN 75 THEN 1
	  	WHEN 100 THEN 2 
	  END  article_consumption_level
	--  CASE max(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT)
	--  	WHEN 75 THEN 1 
	--  ELSE 0 END AS scroll_75,
	--  CASE max(NULLIF(COALESCE(TRIM(regexp_replace(hits_eventinfo_eventlabel, '[^0-9]+.*')) , ''), '')::FLOAT) 
	--  	WHEN 50 THEN 1 
	--  ELSE 0 END AS scroll_50
	FROM gaa.mw_events_201803 
	where hits_eventinfo_eventcategory = 'ArticlePage'  
	group by 
	  trafficsource_referralpath,
	  trafficsource_campaign,
	  trafficsource_medium,
	  trafficsource_source,
	  device_browser,
	  device_browserversion,
	  device_operatingsystem,
	  device_operatingsystemversion,
	  device_devicecategory,
	  device_mobiledevicemodel,
	  geonetwork_country,
	  geonetwork_region,
	  geonetwork_metro,
	  geonetwork_city,
	  hits_page_pagepath,
	  hits_page_pagetitle,
	  hits_appinfo_appname,
	  hits_appinfo_appversion,
	  hits_appinfo_screenname,
	  hits_eventinfo_eventcategory
	limit 50
	

