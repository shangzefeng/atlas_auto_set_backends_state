# atlas_auto_set_backends_state
基于360  atals 的一个 自动化切换 backends state（依据lave的io_thread 和sql_thread 的状态进行切换 ）

atlas_auto_set_backedns_state 主要用于 slave 的复制失败（通过 io_thread、sql-thread来判断）切换 backends 的state的状态。若slave服务停止或者连接不上，atlas_auto_set_backends_state将踢除此slave监控。 若有新的slave须要添加到监控中，需要修改setting.conf的配置信息，并重启atlas_auto_set_backends_state 主程序


setting.conf 是atlas_auto_set_backends_state 的配置文件， 其含有atlas_auto_set_backends_state主程序、slave db、 atlas的管理端的配置信息,详情见配置信息
