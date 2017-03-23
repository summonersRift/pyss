# PYSS: scheduling simulator for high performance computing
Resources: Parallel Workloads archive
   * http://www.cs.huji.ac.il/labs/parallel/workload/


### Run with a workload file downloaded from Parallel WOrkloads archive
   * cd ~/hpc/pyss/src/
   * ./go.sh 4608 input_file FcfsScheduler
      * arg1: num-processors (100 if left blank)
      * arg2: input-file
      * arg3: scheduler

You can run the run_simulator.py if you would like.  
Just run the simulator with --help to see the list of supported schedulers usage.


## python run_simulator.py --help

Psyco not available, will run slower (http://psyco.sourceforge.net)  
   * Usage: run_simulator.py [options]  

Options:
1. -h, --help show this help message and exit
2. --num-processors=NUM_PROCESSORS
..* the number of available processors in the simulated parallel machine
3. --input-file=INPUT_FILE
..* file in the standard workload format: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html, if '-' read from stdin
4. --scheduler=SCHEDULER(OneOfTheFollowingSchedulers)
..1. FcfsScheduler,
..2. ConservativeScheduler,
..3. DoubleConservativeScheduler,
..4. EasyBackfillScheduler,
..5. DoubleEasyBackfillScheduler,
..6. GreedyEasyBackfillScheduler,
..7. EasyPlusPlusScheduler,
..8. ShrinkingEasyScheduler, 
..9. LookAheadEasyBackFillScheduler,
..10. EasySJBFScheduler,
..11. HeadDoubleEasyScheduler,
..12. TailDoubleEasyScheduler,
..13. OrigProbabilisticEasyScheduler,
..14. ReverseEasyScheduler,
..15. PerfectEasyBackfillScheduler,
..16. DoublePerfectEasyBackfillScheduler,
..17. ProbabilisticNodesEasyScheduler,
..18. AlphaEasyScheduler,
..19. DoubleAlphaEasyScheduler
..20. ProbabilisticAlphaEasyScheduler





### Required Softwares:
   * Python 2.4

#### Download Python 2.4 from:
https://www.python.org/ftp/python/2.4/Python-2.4.tar.bz2
in your ~/installation directory

#### There is a bug that might result in error 134 when u make after configure.
To avoid that u might need a BASECFLAGS

 ./configure BASECFLAGS=-U_FORTIFY_SOURCE --prefix=/home/obaida/installation/Python2.4/

#### Then just
  * make 
  * make install

#### Check to see if it is installed properly
  * cd /home/obaida/installation/Python-2.4/bin
  * ./python2.4
  

#### Add this to your PATH
  * vim ~/.bashrc
  * export PATH=$PATH:/home/obaida/installation/Python2.4/bin
  * source ~/.bashrc

Not sure if you need library path as well.




Repository for the Scheduler Simulator.
Work notes are currently in Google Notes, ask Ori Peleg about them.



