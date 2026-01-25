<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import { useRoute } from 'vue-router';
import Axios from '@/plugins/axios';
import store from '@/store';

const route = useRoute();
const message = useMessage();

// 支持课程和班级两种场景
const contentType = computed(() => route.query.content_type || 'course'); // 'course' or 'class'
const objectId = computed(() => Number(route.query.object_id || route.params.id));
const sessionId = computed(() => Number(route.query.session_id));

const loading = ref(false);
const connecting = ref(false);
const joined = ref(false);

const participants = ref([]);

const localAudioStream = ref(null);
const localVideoStream = ref(null);
const localVideoRef = ref(null);

const remoteStreams = ref(new Map());
const videoRefs = ref(new Map());
const audioRefs = ref(new Map());

const ws = ref(null);
const pcs = ref(new Map());

const micOn = ref(true);
const isSharing = ref(false);
const handRaised = ref(false);
const isTeacher = ref(false);

const currentUserId = computed(() => store.state.user?.id);

const iceServers = [
  // STUN 服务器 - 用于发现公网 IP
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  { urls: 'stun:kc.matrixcoding.top:3478' },
  // TURN 服务器 - 自己部署的 coturn
  {
    urls: 'turn:kc.matrixcoding.top:3478',
    username: 'wzyoj',
    credential: 'wzyoj2024turn',
  },
  {
    urls: 'turn:kc.matrixcoding.top:3478?transport=tcp',
    username: 'wzyoj',
    credential: 'wzyoj2024turn',
  },
];

const setVideoRef = (userId, el) => {
  if (!el) return;
  videoRefs.value.set(userId, el);
  const s = remoteStreams.value.get(userId);
  if (s) {
    console.log('setVideoRef: Binding existing stream to video element for user', userId);
    el.srcObject = s;
    el.play().catch(err => console.warn('Failed to play video in setVideoRef:', err));
  }
};

const ensureLocalAudio = async () => {
  if (localAudioStream.value) return;
  
  try {
    const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    localAudioStream.value = audioStream;
    console.log('Audio stream obtained');
    return audioStream;
  } catch (err) {
    message.error(`无法获取麦克风: ${err.message}`);
    throw err;
  }
};

const startScreenShare = async () => {
  if (localVideoStream.value) return;
  
  if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
    message.error('您的浏览器不支持屏幕共享功能，或当前页面不是 HTTPS 安全连接。');
    throw new Error('getDisplayMedia not supported');
  }
  
  try {
    const displayStream = await navigator.mediaDevices.getDisplayMedia({ 
      video: { displaySurface: 'monitor' },
      audio: true 
    });
    
    localVideoStream.value = displayStream;
    isSharing.value = true;
    
    console.log('Screen share stream obtained:', {
      videoTracks: displayStream.getVideoTracks().length,
      audioTracks: displayStream.getAudioTracks().length
    });
    
    // Wait for DOM to update
    await nextTick();
    
    // Set video source
    if (localVideoRef.value) {
      console.log('Setting video srcObject');
      localVideoRef.value.srcObject = displayStream;
      
      await new Promise((resolve) => {
        localVideoRef.value.onloadedmetadata = () => {
          console.log('Video metadata loaded, dimensions:', 
            localVideoRef.value.videoWidth, 'x', localVideoRef.value.videoHeight);
          resolve();
        };
        setTimeout(resolve, 1000);
      });
      
      try {
        await localVideoRef.value.play();
        console.log('Local video playing successfully');
      } catch (err) {
        console.warn('Failed to play local video:', err);
        setTimeout(async () => {
          try {
            await localVideoRef.value.play();
          } catch (e) {
            console.error('Still failed to play:', e);
          }
        }, 500);
      }
    } else {
      console.error('localVideoRef is null after nextTick!');
    }
    
    // Handle screen share stop
    displayStream.getVideoTracks()[0].onended = () => {
      stopScreenShare();
    };
    
    // Add video tracks to all peer connections and renegotiate
    for (const [userId, pc] of pcs.value.entries()) {
      displayStream.getTracks().forEach(track => {
        pc.addTrack(track, displayStream);
      });
      
      // Trigger renegotiation to send the new tracks
      renegotiate(userId, pc);
    }
  } catch (err) {
    message.error(`无法共享屏幕: ${err.message}`);
    throw err;
  }
};

const renegotiate = async (otherUserId, pc) => {
  try {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    sendSignal(otherUserId, 'offer', offer);
    console.log('Renegotiation offer sent to user', otherUserId);
  } catch (err) {
    console.error('Renegotiation failed:', err);
  }
};

const stopScreenShare = () => {
  if (localVideoStream.value) {
    localVideoStream.value.getTracks().forEach(track => track.stop());
    localVideoStream.value = null;
  }
  isSharing.value = false;
  if (localVideoRef.value) localVideoRef.value.srcObject = null;
};

const leaveSession = () => {
  // Stop audio
  if (localAudioStream.value) {
    localAudioStream.value.getTracks().forEach(track => track.stop());
    localAudioStream.value = null;
  }
  
  // Stop video
  stopScreenShare();
  
  // Close all peer connections
  for (const [userId, pc] of pcs.value.entries()) {
    closePeer(userId);
  }
  
  // Disconnect websocket
  if (ws.value) {
    ws.value.close();
    ws.value = null;
  }
  joined.value = false;
};

const closePeer = (otherUserId) => {
  const pc = pcs.value.get(otherUserId);
  if (pc) {
    try {
      pc.close();
    } catch {
      // ignore
    }
  }
  pcs.value.delete(otherUserId);
  remoteStreams.value.delete(otherUserId);
  const el = videoRefs.value.get(otherUserId);
  if (el) {
    try {
      el.srcObject = null;
    } catch {
      // ignore
    }
  }
};

const sendSignal = (toUserId, signalType, data) => {
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;
  ws.value.send(JSON.stringify({
    type: 'signal',
    to_user_id: toUserId,
    signal_type: signalType,
    data,
  }));
};

const createPeerConnection = async (otherUserId) => {
  if (pcs.value.get(otherUserId)) return pcs.value.get(otherUserId);

  console.log('Creating peer connection with ICE servers:', iceServers);
  const pc = new RTCPeerConnection({ iceServers });
  pcs.value.set(otherUserId, pc);
  
  // 监听 ICE 连接状态变化
  pc.oniceconnectionstatechange = () => {
    console.log('ICE connection state with user', otherUserId, ':', pc.iceConnectionState);
  };
  
  // 监听 ICE 收集状态
  pc.onicegatheringstatechange = () => {
    console.log('ICE gathering state with user', otherUserId, ':', pc.iceGatheringState);
  };

  // Add local audio stream (everyone has audio)
  if (localAudioStream.value) {
    localAudioStream.value.getTracks().forEach((t) => pc.addTrack(t, localAudioStream.value));
  }
  
  // Add local video stream (only if sharing screen)
  if (localVideoStream.value) {
    localVideoStream.value.getTracks().forEach((t) => pc.addTrack(t, localVideoStream.value));
  }

  pc.onicecandidate = (e) => {
    if (!e.candidate) return;
    sendSignal(otherUserId, 'ice', e.candidate);
  };

  pc.ontrack = (e) => {
    const stream = e.streams?.[0];
    if (!stream) return;
    
    console.log('Received track from user', otherUserId, 'kind:', e.track.kind, 'stream id:', stream.id);
    
    // Store the stream
    remoteStreams.value.set(otherUserId, stream);
    
    // Function to set stream to elements with retry
    const setStreamToElements = async (retryCount = 0) => {
      await nextTick();
      
      // Set to video element if it's a video track
      if (e.track.kind === 'video') {
        const el = videoRefs.value.get(otherUserId);
        if (el) {
          console.log('Setting video srcObject for user', otherUserId);
          el.srcObject = stream;
          try {
            await el.play();
            console.log('Remote video playing for user', otherUserId);
          } catch (err) {
            console.warn('Failed to play remote video:', err);
          }
        } else if (retryCount < 5) {
          // Retry after a short delay if element not found
          console.log('Video element not found, retrying...', retryCount + 1);
          setTimeout(() => setStreamToElements(retryCount + 1), 500);
        }
      }
      
      // Set to audio element if it's an audio track
      if (e.track.kind === 'audio') {
        const audioEl = audioRefs.value.get(otherUserId);
        if (audioEl) {
          console.log('Setting audio srcObject for user', otherUserId);
          audioEl.srcObject = stream;
          try {
            await audioEl.play();
            console.log('Remote audio playing for user', otherUserId);
          } catch (err) {
            console.warn('Failed to play remote audio:', err);
          }
        } else if (retryCount < 5) {
          console.log('Audio element not found, retrying...', retryCount + 1);
          setTimeout(() => setStreamToElements(retryCount + 1), 500);
        }
      }
    };
    
    setStreamToElements();
  };

  pc.onconnectionstatechange = () => {
    const st = pc.connectionState;
    console.log('Peer connection state with user', otherUserId, ':', st);
    if (st === 'failed' || st === 'closed' || st === 'disconnected') {
      // keep a bit tolerant; user_left event will cleanup
    }
  };

  return pc;
};

const maybeCall = async (otherUserId) => {
  const me = currentUserId.value;
  if (!me || me === otherUserId) return;

  // Deterministic initiator to avoid glare: only lower ID initiates
  if (me >= otherUserId) {
    console.log('maybeCall: Skipping call to user', otherUserId, '(my ID:', me, 'is >= their ID)');
    return;
  }

  console.log('maybeCall: Initiating call to user', otherUserId);
  const pc = await createPeerConnection(otherUserId);
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  sendSignal(otherUserId, 'offer', offer);
  console.log('maybeCall: Offer sent to user', otherUserId);
};

const handleSignal = async (payload) => {
  const from = payload.from_user_id;
  const signalType = payload.signal_type;
  const data = payload.data;

  if (!from || from === currentUserId.value) return;

  const pc = await createPeerConnection(from);

  if (signalType === 'offer') {
    await pc.setRemoteDescription(data);
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    sendSignal(from, 'answer', answer);
    return;
  }

  if (signalType === 'answer') {
    await pc.setRemoteDescription(data);
    return;
  }

  if (signalType === 'ice') {
    try {
      await pc.addIceCandidate(data);
    } catch {
      // ignore
    }
  }
};

const joinSession = async () => {
  if (!sessionId.value) {
    message.error('缺少 session_id');
    return;
  }

  connecting.value = true;
  try {
    await ensureLocalAudio();
  } catch (err) {
    connecting.value = false;
    return;
  }
  
  try {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/live/${sessionId.value}/`;
    
    console.log('Connecting to WebSocket:', url);

    const socket = new WebSocket(url);
    ws.value = socket;

    socket.onopen = () => {
      console.log('WebSocket connected successfully');
      joined.value = true;
      connecting.value = false;
    };

    socket.onmessage = async (e) => {
      let data;
      try {
        data = JSON.parse(e.data);
      } catch {
        return;
      }
      
      console.log('WebSocket message received:', data.type);

      if (data.type === 'participants') {
        participants.value = data.participants || [];
        console.log('Participants updated:', participants.value);
        const ids = participants.value.map((p) => p.user_id);
        // cleanup peers that are gone
        for (const otherId of Array.from(pcs.value.keys())) {
          if (!ids.includes(otherId)) closePeer(otherId);
        }
        // create peers for new
        for (const otherId of ids) {
          if (otherId === currentUserId.value) continue;
          await maybeCall(otherId);
        }
        return;
      }

      if (data.type === 'user_joined') {
        // user_joined 事件包含 user 对象，而不是直接的 user_id
        const joinedUserId = data.user?.user_id || data.user_id;
        console.log('User joined:', joinedUserId, 'data:', data);
        // When a new user joins, try to establish connection
        if (joinedUserId && joinedUserId !== currentUserId.value) {
          await maybeCall(joinedUserId);
        }
        return;
      }

      if (data.type === 'user_left') {
        console.log('User left:', data.user_id);
        closePeer(data.user_id);
        return;
      }

      if (data.type === 'signal') {
        console.log('Signal received:', data.signal_type, 'from:', data.from_user_id);
        await handleSignal(data);
      }
    };

    socket.onclose = (ev) => {
      console.log('WebSocket closed:', ev?.code, ev?.reason);
      ws.value = null;
      joined.value = false;
      if (ev?.code === 4429) message.error('直播间人数已满（最多5人）');
    };
    
    socket.onerror = (err) => {
      message.error('WebSocket 连接失败');
      console.error('WebSocket error:', err);
      connecting.value = false;
    };
  } catch (err) {
    message.error(`连接失败: ${err.message}`);
    console.error('Connect error:', err);
    connecting.value = false;
  }
};

const toggleMic = () => {
  micOn.value = !micOn.value;
  localAudioStream.value?.getAudioTracks()?.forEach((t) => {
    t.enabled = micOn.value;
  });
  console.log('Microphone', micOn.value ? 'enabled' : 'disabled');
};

const handleScreenShare = async () => {
  if (!isTeacher.value) {
    message.warning('只有老师可以共享屏幕');
    return;
  }
  
  if (isSharing.value) {
    stopScreenShare();
  } else {
    try {
      await startScreenShare();
    } catch (err) {
      console.error('Failed to start screen share:', err);
    }
  }
};

const toggleHand = () => {
  handRaised.value = !handRaised.value;
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({ type: 'raise_hand', hand_raised: handRaised.value }));
  }
};

const init = async () => {
  loading.value = true;
  try {
    // Get session info to determine if user is teacher
    const res = await Axios.get(`/live/session/${sessionId.value}/`);
    const session = res.session;
    if (!session) {
      message.error('直播不存在');
      return;
    }
    
    // Check if current user is teacher
    // 支持 related_object（新格式）和 course（旧格式）
    const relatedObj = session.related_object || session.course;
    isTeacher.value = relatedObj?.teacher_id === currentUserId.value;
    console.log('Is teacher:', isTeacher.value);
    console.log('Content type:', contentType.value);
    
    // Auto-join session with audio
    await joinSession();
  } catch (err) {
    console.error('Init error:', err);
    message.error('初始化失败');
  } finally {
    loading.value = false;
  }
};

init();

onBeforeUnmount(() => {
  leaveSession();
});
</script>

<template>
  <n-spin :show="loading">
    <div>
      <n-space align="center" justify="space-between">
        <h1 style="margin: 0">直播课堂</h1>
        <n-space>
          <n-button v-if="isTeacher && !isSharing" type="primary" @click="handleScreenShare">
            开始共享屏幕
          </n-button>
          <n-button v-if="isTeacher && isSharing" type="error" @click="handleScreenShare">
            停止共享
          </n-button>
          <n-button secondary @click="toggleMic">
            {{ micOn ? '🎤 麦克风开启' : '🔇 麦克风关闭' }}
          </n-button>
          <n-button secondary @click="toggleHand">{{ handRaised ? '🙋 放下手' : '✋ 举手' }}</n-button>
          <n-button v-if="joined" type="error" secondary @click="leaveSession">离开直播</n-button>
        </n-space>
      </n-space>

      <n-alert v-if="!sessionId" type="warning" style="margin-top: 12px">
        缺少 session_id，请从课程页进入直播。
      </n-alert>

      <!-- Teacher's screen share (large display) -->
      <n-card v-if="isSharing" size="small" title="我的屏幕共享" style="margin-top: 12px">
        <video ref="localVideoRef" autoplay playsinline muted style="width: 100%; background: #000; max-height: 70vh;" />
      </n-card>

      <!-- Remote screens (teacher's screen for students) -->
      <template v-for="p in participants" :key="p.user_id">
        <n-card
          v-if="p.user_id !== currentUserId && p.role === 'teacher'"
          size="small"
          :title="`${p.username} 的屏幕共享`"
          style="margin-top: 12px"
        >
          <video
            :ref="(el) => setVideoRef(p.user_id, el)"
            autoplay
            playsinline
            style="width: 100%; background: #000; max-height: 70vh;"
          />
        </n-card>
        
        <!-- Audio element for each remote participant (always rendered) -->
        <audio
          v-if="p.user_id !== currentUserId"
          :ref="(el) => { if (el) audioRefs.set(p.user_id, el); }"
          autoplay
          style="display: none;"
        />
      </template>

      <n-card size="small" title="在线成员" style="margin-top: 12px">
        <n-alert v-if="joined" type="success" style="margin-bottom: 12px">
          已连接到直播间，{{ micOn ? '麦克风已开启' : '麦克风已关闭' }}
        </n-alert>
        <n-space wrap>
          <n-tag v-for="p in participants" :key="p.user_id" :type="p.role === 'teacher' ? 'success' : 'default'">
            {{ p.username }}
            <span v-if="p.role === 'teacher'"> 👨‍🏫</span>
            <span v-if="p.hand_raised"> 🙋</span>
            <span v-if="p.user_id === currentUserId"> (我)</span>
          </n-tag>
        </n-space>
      </n-card>
    </div>
  </n-spin>
</template>
