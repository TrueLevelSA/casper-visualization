#!/usr/bin/env bash

function kill_children {
    echo "Stopping loggers"

    # sends a SIGINT to all the children processes from this
    # $$ returns curent PID
    pkill --signal SIGTERM -P $$

    echo "Waiting for logger instances to terminate."

    #waits for all children to terminate
    wait

    echo "Everything should have finished gracefully."
}

function main {
    # calls kill_children on exit
    trap kill_children EXIT

    local -r LOG_PATH=logs
    mkdir -p $LOG_PATH

    local -r LOG_INTERVAL_SECONDS="1"

    local -r DATE=$(date +"%y-%m-%d_%H-%M-%S_")
    local -r LOG_CPU=$LOG_PATH/${DATE}cpu.log
    local -r LOG_MEM=$LOG_PATH/${DATE}mem.log
    # processor
    pidstat -C "generative_test.*" $LOG_INTERVAL_SECONDS -T ALL > $LOG_CPU &
    # memor
    pidstat -C "generative_test.*" $LOG_INTERVAL_SECONDS -r -T ALL > $LOG_MEM &

    echo "Logging started"
    sleep 100000000
}

main
