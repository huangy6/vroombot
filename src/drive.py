from libs import *
import create


class NotEnoughHands(Exception):
	pass


class SampleListener(Leap.Listener):
	global initial_hands_pos
	initial_hands_pos = False
	global robot
	robot = create.Create("/dev/ttyUSB0")
	robot.toFullMode()
	
	def on_connect(self, controller):
		print "Connected"
		# foo()

	def on_frame(self, controller):
		global robot
		global initial_hands_pos
		global counter
		frame = controller.frame() 
		try:
			if not initial_hands_pos: 
				initial_hands_pos = get_hand_pos(frame)
				print initial_hands_pos
				print "Not Calculated"
			else:
				lh_pos, rh_pos = get_hand_pos(frame)
				lh_offset, rh_offset = get_offsets((lh_pos, rh_pos), initial_hands_pos)
				lh_zdist = lh_offset[2]
				rh_zdist = rh_offset[2]
				if lh_zdist > rh_zdist:
					robot.go(lh_zdist, (rh_zdist - lh_zdist)*360/200)
				else:
					robot.go(rh_zdist, (rh_zdist - lh_zdist)*360/200)
				print "Calculated"
				print str(lh_zdist)+","+str(rh_zdist)
				
		except NotEnoughHands:
			print "Two hands on the wheel!"
			robot.stop()

		"""print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
			frame.id,
			frame.timestamp,
			len(frame.hands),
			len(frame.fingers),
			len(frame.tools),
			len(frame.gestures()))"""
				
def get_offsets(current_hands_pos, initial_hands_pos):
	"""Finds left and right hand offsets
	"""
	curr_lh, curr_rh = current_hands_pos
	init_lh, init_rh = initial_hands_pos

	return(-(curr_lh - init_lh), -(curr_rh - init_rh))


def get_hands(frame):
	"""Returns left and right hands from a frame
	"""
	lh, rh = frame.hands
	if not lh.is_left:
		# Switch hands if hands do not match
		rh_t = rh
		rh = lh
		lh = rh_t

	return(lh, rh)


def get_hand_pos(frame):
	"""returns left hand, right hand
	"""
	if len(frame.hands) != 2:
		raise NotEnoughHands

	lh, rh = get_hands(frame)

	return(lh.palm_position, rh.palm_position)


def main():
	# Create a sample listener and controller
	listener = SampleListener()
	controller = Leap.Controller()

	# Have the sample listener receive events from the controller
	controller.add_listener(listener)


	# Keep this process running until Enter is pressed
	print "Press Enter to quit..."
	try:
		sys.stdin.readline()
	except KeyboardInterrupt:
		pass
	finally:
		# Remove the sample listener when done
		controller.remove_listener(listener)
		robot.stop()

if __name__ == "__main__":
	main()
