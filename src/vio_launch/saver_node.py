import os, abc, time
import rospy
from std_srvs.srv import Empty, EmptyResponse
from opensimrt_msgs.srv import SetFileNameSrv, SetFileNameSrvResponse


class SaverNodeBase(abc.ABC):
    """Python twin of Ros::SaverNode. Subclass and implement save()."""

    def __init__(self):
        self.recording = False
        self.recording_count = 0
        self.resolved_file_prefix = ""
        self.notes = ""
        self.description = ""
        self._epoch_start = rospy.get_param("~epoch_start", 0.0)
        self._recording_enabled = False

    def on_init(self):
        rospy.Service("~start_recording",  Empty, self._start_recording)
        rospy.Service("~stop_recording",   Empty, self._stop_recording)
        rospy.Service("~clear_loggers",    Empty, self._clear_loggers)
        rospy.Service("~write_csv",        Empty, self._write_csv)
        rospy.Service("~write_sto",        Empty, self._write_sto)
        rospy.Service("~set_name_and_path", SetFileNameSrv, self._set_name_path)
        rospy.Timer(rospy.Duration(0.1), self._time_check)

    # --- params, read fresh each time like the C++ does
    def data_save_dir(self):
        return rospy.get_param("~data_save_dir", "/tmp/")

    def data_save_filename(self):
        return rospy.get_param("~data_save_file", "file")

    def is_recording(self):
        return self._recording_enabled and self.recording

    # --- service handlers
    def _start_recording(self, req):
        rospy.loginfo("startRecording service called.")
        self.recording = True
        return EmptyResponse()

    def _stop_recording(self, req):
        rospy.loginfo("stopRecording service called.")
        self.recording_count += 1
        self.recording = False
        return EmptyResponse()

    def _clear_loggers(self, req):
        self.clear()
        return EmptyResponse()

    def _write_csv(self, req):
        self.save("csv")
        return EmptyResponse()

    def _write_sto(self, req):
        self.save("sto")
        return EmptyResponse()

    def _set_name_path(self, req):
        rospy.set_param("~data_save_dir", req.path)
        rospy.set_param("~data_save_file", req.name)
        self.notes = req.notes
        self.description = req.description
        data_save_dir = self.data_save_dir()
        ## we are not going to do the tilde expansion, why did i even?
        if not os.path.exists(data_save_dir):
            os.makedirs(data_save_dir)
        
        self.resolved_file_prefix = data_save_dir + "/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
        
        return SetFileNameSrvResponse()

    def _time_check(self, event):
        self._recording_enabled = rospy.Time.now().to_sec() >= self._epoch_start

    # --- subclass fills these
    @abc.abstractmethod
    def save(self, kind):
        if not self.notes == "" or not self.description == "":
            rospy.logwarn("I am not sure what to do with notes or descriptions on regular saves, not sure if they will be saved!")

    @abc.abstractmethod
    def clear(self):
        pass
