#!/bin/bash

nohup /home/log_analysis/elasticsearch-1.7.5/bin/elasticsearch & disown
echo "Elasticsearch is UP"
