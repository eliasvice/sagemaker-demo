cat scroll_traffic.test.small | awk -F '|' '{if(NF>19) print NF, NR;}' 
cat scroll_traffic.train.small | awk -F '|' '{if(NF>19) print NF, NR;}'
# ----- Here replace pipes in text (not a separator) with a dash - or some other character
sed -ie 's/\"//g' scroll_traffic.train.small 
sed -ie 's/\"//g' scroll_traffic.test.small

# To check the percentage of the most dominant class
cat scroll_traffic.test.small | awk -F '|' '{ if ($19==2) count++; } END { print count/NR; }'

cat scroll_traffic.train.small | awk -F '|' '{ if ($19==2) count++; } END { print count/NR; }'

# The following prints lines where class != 2
# These can be concatenated to the existing training and testing datasets

cat scroll_traffic_0000_part_00 | awk -F '|' '{ if ($19!=0) print }' > class_0_samples 
wc -l class_0_samples
cat scroll_traffic_0000_part_00 | awk -F '|' '{ if ($19!=1) print }' > class_1_samples
wc -l class_1_samples                                                                 
cat scroll_traffic_0000_part_00 | awk -F '|' '{ if ($19!=2) print }' > class_2_samples
wc -l class_2_samples


head -10000 class_0_samples > scroll_traffic.train.small
head -10000 class_1_samples >> scroll_traffic.train.small
head -15000 class_2_samples >> scroll_traffic.train.small

# Take  more proportional samples
tail -3000 class_0_samples > scroll_traffic.valid.small 
tail -3000 class_1_samples > scroll_traffic.valid.small
tail -5000 class_2_samples > scroll_traffic.valid.small

                                                                
# This limit the number of lines to check before stopping so that we don't go thru everything

cat scroll_traffic.train.small | awk -F '|' '{if(NF<=19) print}' > scroll.train.small
cat scroll_traffic.valid.small | awk -F '|' '{if(NF<=19) print}' > scroll.valid.small
cat scroll_traffic.test.small | awk -F '|' '{if(NF<=19) print}' > scroll.test.small
