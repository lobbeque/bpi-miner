#!/bin/bash

exitWithUsage()
{
    echo "$1" 1>&2
    usage
    exit 1
}


usage()
{
    cat << EOF

USAGE: `basename $0` options

OPTIONS:
   --days (required) number of days before remove : 10 or 100 or ...
   --type (required) [elasticsearch|index]
   --help (optional)

EOF
}


init()
{

    while getopts ":-:" OPTION
    do
        LONG_OPTION="${OPTARG%%=*}"
        OPTARG="${OPTARG#*=}"

        case $LONG_OPTION in
            days) 
                DAYS=${OPTARG}
                ;;

            type) 
                TYPE=${OPTARG}
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

    if [ "${DAYS}" = "" ] || [ "${TYPE}" = "" ]; then
        exitWithUsage "a required option is missing."
    fi

    

    if ["${TYPE}" = "elasticsearch" ]; then
		find /data/elasticsearch_logs -mtime +${DAYS} -type f -delete
    	echo "elasticsearch logs older than ${DAYS} deleted"
    elif ["${TYPE}" = "index" ]; then
    	find /data/index_logs -mtime +${DAYS} -type f -delete
    	echo "index logs older than ${DAYS} deleted"
    fi   
}


init "$@"
