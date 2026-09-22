#!/usr/bin/env python3
"""Copy chrony's logs into the take directory, so a recording can be
audited afterwards for steps, slew and chronyd dying mid-take."""

import os
import shutil

import rospy

from vio_launch.saver_node import SaverNodeBase

CHRONY_LOGDIR = "/var/log/chrony"


class ChronyLogSaver(SaverNodeBase):

    def __init__(self):
        super().__init__()
        self.logdir = rospy.get_param("~chrony_logdir", CHRONY_LOGDIR)

    def save(self, kind):
        if not self.resolved_file_prefix:
            rospy.logerr("set_name_and_path was never called; refusing to save "
                         "to the current working directory.")
            return

        dest = "{}{}{}_chrony".format(self.resolved_file_prefix,
                                      self.data_save_filename(),
                                      self.recording_count)
        if os.path.isdir(dest):
            rospy.loginfo("%s already copied this take, skipping.", dest)
            return

        try:
            shutil.copytree(self.logdir, dest)
        except PermissionError:
            rospy.logerr("cannot read %s. Add this user to the _chrony group "
                         "(and --group-add it into the container).", self.logdir)
            return
        except OSError as e:
            rospy.logerr("copying %s failed: %s", self.logdir, e)
            return

        n = len(os.listdir(dest))
        rospy.loginfo("saved %d chrony log files to %s", n, dest)

    def clear(self):
        pass

if __name__ == "__main__":
    rospy.init_node("chrony_log_saver")
    node = ChronyLogSaver()
    node.on_init()
    rospy.loginfo("chrony log saver ready.")
    rospy.spin()
