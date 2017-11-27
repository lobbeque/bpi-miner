#!/bin/bash

nohup /home/log_analysis/elasticsearch-1.7.5/bin/elasticsearch & disown
echo "Elasticsearch is UP"
sleep 30
nohup /home/log_analysis/kibana-4.1.5-linux-x64/bin/kibana & disown
echo "kibana is UP"
