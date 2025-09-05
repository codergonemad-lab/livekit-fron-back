import React, { useState, useEffect, useRef } from 'react';
import { Room, connect, createLocalTracks } from 'livekit-client';

const VideoCall = () => {
  const [room, setRoom] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [localTracks, setLocalTracks] = useState([]);
  const [participants, setParticipants] = useState([]);
  const videoContainerRef = useRef(null);

  // Your LiveKit configuration
  const LIVEKIT_URL = 'wss://osadho-m62vhfz7.livekit.cloud';
  const LIVEKIT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6IiIsIm5hbWUiOiJzYWtldCIsInZpZGVvIjp7InJvb21DcmVhdGUiOmZhbHNlLCJyb29tTGlzdCI6ZmFsc2UsInJvb21SZWNvcmQiOmZhbHNlLCJyb29tQWRtaW4iOmZhbHNlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fYWJmMmI3MGEiLCJjYW5QdWJsaXNoIjp0cnVlLCJjYW5TdWJzY3JpYmUiOnRydWUsImNhblB1Ymxpc2hEYXRhIjp0cnVlLCJjYW5QdWJsaXNoU291cmNlcyI6W10sImNhblVwZGF0ZU93bk1ldGFkYXRhIjpmYWxzZSwiaW5ncmVzc0FkbWluIjpmYWxzZSwiaGlkZGVuIjpmYWxzZSwicmVjb3JkZXIiOmZhbHNlLCJhZ2VudCI6ZmFsc2V9LCJzaXAiOnsiYWRtaW4iOmZhbHNlLCJjYWxsIjpmYWxzZX0sIm1ldGFkYXRhIjoiIiwic2hhMjU2IjoiIiwic3ViIjoic2FrZXQiLCJpc3MiOiJBUEkzcGg0ejlLMkx5RTUiLCJuYmYiOjE3NTcwODExOTAsImV4cCI6MTc1NzEwMjc5MH0.VmICVEuLo7TocYf7AeR41YQ97I6pWK_jzWrMqxVJ5C8';

  const connectToRoom = async () => {
    try {
      const roomInstance = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      // Set up event listeners
      roomInstance.on('trackSubscribed', (track, publication, participant) => {
        console.log('Track subscribed:', track, participant);
        if (track.kind === 'video' || track.kind === 'audio') {
          const element = track.attach();
          videoContainerRef.current?.appendChild(element);
        }
      });

      roomInstance.on('trackUnsubscribed', (track, publication, participant) => {
        track.detach();
      });

      roomInstance.on('disconnected', () => {
        setIsConnected(false);
        setRoom(null);
      });

      // Connect to room
      await roomInstance.connect(LIVEKIT_URL, LIVEKIT_TOKEN);
      setRoom(roomInstance);
      setIsConnected(true);

      // Enable camera and microphone
      const tracks = await createLocalTracks({
        audio: true,
        video: true,
      });

      // Publish tracks
      for (const track of tracks) {
        await roomInstance.localParticipant.publishTrack(track);
      }

      setLocalTracks(tracks);

    } catch (error) {
      console.error('Failed to connect:', error);
    }
  };

  const disconnectFromRoom = async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
      setIsConnected(false);
      setLocalTracks([]);
    }
  };

  const toggleCamera = async () => {
    const videoTrack = localTracks.find(track => track.kind === 'video');
    if (videoTrack) {
      if (videoTrack.isMuted) {
        await videoTrack.unmute();
      } else {
        await videoTrack.mute();
      }
    }
  };

  const toggleMicrophone = async () => {
    const audioTrack = localTracks.find(track => track.kind === 'audio');
    if (audioTrack) {
      if (audioTrack.isMuted) {
        await audioTrack.unmute();
      } else {
        await audioTrack.mute();
      }
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>LiveKit Video Call</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={connectToRoom} disabled={isConnected}>
          Connect to Room
        </button>
        <button onClick={disconnectFromRoom} disabled={!isConnected}>
          Disconnect
        </button>
        <button onClick={toggleCamera} disabled={!isConnected}>
          Toggle Camera
        </button>
        <button onClick={toggleMicrophone} disabled={!isConnected}>
          Toggle Microphone
        </button>
      </div>

      <div 
        ref={videoContainerRef}
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '10px'
        }}
      >
        {/* Video elements will be added here dynamically */}
      </div>
    </div>
  );
};

export default VideoCall;
