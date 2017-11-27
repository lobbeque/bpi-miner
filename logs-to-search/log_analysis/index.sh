#!/bin/bash

exitWithUsage()
{
	echo "$1" >> ${log_file}
    echo "$1" 1>&2
    usage
    exit 1
}


usage()
{
    cat << EOF

USAGE: `basename $0` options

OPTIONS:
   --date (required ) periode "AAAA-MM-jj AAAA-MM-jj" | or single "AAAA-MM-j"
   --help (optional)

EOF
}


init()
{

	# Create log file for this indexation 

	current_date=$(date +"%Y-%m-%dT%XZ")
	log_file="/data/index_logs/index_logs_${current_date}.log"
	touch ${log_file}

    while getopts ":-:" OPTION
    do
        LONG_OPTION="${OPTARG%%=*}"
        OPTARG="${OPTARG#*=}"

        case $LONG_OPTION in
            date) 
                DATE=${OPTARG}
                ;;

            help) 
                usage ; 
                exit 0
                ;;

            *) 
                echo "Unknown option ${LONG_OPTION}" ; 
                usage ; 
                exit 1 
                ;;
        esac
    done

    if [ "${DATE}" = "" ]; then
        exitWithUsage "a required option is missing."
    fi

    IFS=' ' read -r -a PERIODE <<< "$DATE"

    FROM=$(date -I -d "${PERIODE[0]}") || exitWithUsage "wrong date format, should be AAAA-MM-jj"

	if [ -z "${PERIODE[1]}" ] 
		then TO=$FROM
	else 
		TO=$(date -I -d "${PERIODE[1]}") || exitWithUsage "wrong date format, should be AAAA-MM-jj"
	fi   
}


index()
{

	DATES=()
	D="$FROM"
	DATES+=( "$D" )
	
	while [ "$D" != "$TO" ]; do
	  D=$(date -I -d "$D + 1 day")
	  DATES+=( "$D" )
	done

	for i in "${DATES[@]}"
	do

		fileolfeo=/data/logs_proxy/olfeo_ncsa_${i}.log.bz2
		
		if [ ! -f $fileolfeo ]
		  then
		    echo "les logs olfeo du $i n'existent pas, passer à la date suivante" 
		    continue
		fi
		
		logstash_path=/home/log_analysis/logstash-2.2.0
		
		echo "starting logstash "
		
		date +"%T"
		
		echo "Creation de l'index bpi_logs du $i $fileolfeo"

		echo "bzcat -s $fileolfeo | ${logstash_path}/bin/logstash -f ${logstash_path}/bin/log_config/bpi_logs.conf  -l /dev/null &>/dev/null"
		
		bzcat -s $fileolfeo | ${logstash_path}/bin/logstash -f ${logstash_path}/bin/log_config/bpi_logs.conf  -l /dev/null | echo
		
                #bzcat -s $fileolfeo | ${logstash_path}/bin/logstash -f ${logstash_path}/bin/log_config/bpi_logs.conf

		echo "Refresh"

		curl -XPOST http://localhost:9200/_refresh
	done
	
	echo "end"
	
	date +"%T"
}

init "$@"

index
