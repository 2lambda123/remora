#!/bin/bash

# -- Collect required data in backgroud

source $REMORA_OUTDIR/remora_env.txt

PID=(); PID_MIC=()
idx=0
for NODE in $NODES
do
  #This is the core of REMORA. It connects to all the nodes allocated to this job and runs the remora_report.sh script
  #remora_report.sh will run an infinite loop where, in each iteration of the loop, it calls the different modules
  #that are available (specified in the configuration file)
  COMMAND="$REMORA_BIN/scripts/remora_report.sh $NODE $REMORA_BIN $REMORA_OUTDIR 1>> $REMORA_OUTDIR/.remora_out_$NODE 2>> $REMORA_OUTDIR/.remora_out_$NODE & echo \$!"

  if [ "$REMORA_VERBOSE" == "1" ]; then
    echo ""; echo "ssh -f -n $NODE $COMMAND"
  fi

  #We have to capture the PID of the remote process running remora_report.sh
  #Since the script is an inifinite loop, we have to kill the process once the job
  #that we are analyzing has finished
  PID[$idx]=`ssh -f -n $NODE $COMMAND 2> /dev/null | sed -e's/\[.*\]//' `

  #Repeat the same for the MIC
  if [ "$REMORA_SYMMETRIC" == "1" ]; then
    COMMAND="$REMORA_BIN/scripts/remora_report_mic.sh ${NODE}-mic0 $REMORA_OUTDIR $REMORA_EFFECTIVE_PERIOD $REMORA_SYMMETRIC $REMORA_MODE $REMORA_PARALLEL $REMORA_VERBOSE $REMORA_BIN > $REMORA_OUTDIR/.remora_out_$NODE-mic0  &  echo \$! "
    if [ "$REMORA_VERBOSE" == "1" ]; then
        echo "ssh -q -f -n $NODE-mic0 $COMMAND"
    fi  
    PID_MIC[$idx]=`ssh -q -f -n $NODE-mic0 $COMMAND `
  fi  
  #Go to the next node
  idx=$((idx+1))
done
echo ${PID[@]} > $REMORA_OUTDIR/remora_pid.txt
echo ${PID_MIC[@]} > $REMORA_OUTDIR/remora_pid_mic.txt

# Only do this is MONITOR mode is active
if [ "$REMORA_MODE" == "MONITOR" ]; then
	NODE=`hostname -s`
	PID=`$REMORA_BIN/scripts/remora_monitor.sh $NODE $REMORA_BIN $REMORA_OUTDIR 1> /dev/null 2> /dev/null & echo $! > $REMORA_OUTDIR/remora_pid_monitor.txt`
fi