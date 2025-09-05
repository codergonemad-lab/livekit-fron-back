// React Native example
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { connect, Room } from '@livekit/react-native';
import { VideoView, AudioSession } from '@livekit/react-native';

const VideoCallScreen = () => {
  const [room, setRoom] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Your LiveKit configuration
  const LIVEKIT_URL = 'wss://osadho-m62vhfz7.livekit.cloud';
  const LIVEKIT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6IiIsIm5hbWUiOiJzYWtldCIsInZpZGVvIjp7InJvb21DcmVhdGUiOmZhbHNlLCJyb29tTGlzdCI6ZmFsc2UsInJvb21SZWNvcmQiOmZhbHNlLCJyb29tQWRtaW4iOmZhbHNlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6InJvb21fYWJmMmI3MGEiLCJjYW5QdWJsaXNoIjp0cnVlLCJjYW5TdWJzY3JpYmUiOnRydWUsImNhblB1Ymxpc2hEYXRhIjp0cnVlLCJjYW5QdWJsaXNoU291cmNlcyI6W10sImNhblVwZGF0ZU93bk1ldGFkYXRhIjpmYWxzZSwiaW5ncmVzc0FkbWluIjpmYWxzZSwiaGlkZGVuIjpmYWxzZSwicmVjb3JkZXIiOmZhbHNlLCJhZ2VudCI6ZmFsc2V9LCJzaXAiOnsiYWRtaW4iOmZhbHNlLCJjYWxsIjpmYWxzZX0sIm1ldGFkYXRhIjoiIiwic2hhMjU2IjoiIiwic3ViIjoic2FrZXQiLCJpc3MiOiJBUEkzcGg0ejlLMkx5RTUiLCJuYmYiOjE3NTcwODExOTAsImV4cCI6MTc1NzEwMjc5MH0.VmICVEuLo7TocYf7AeR41YQ97I6pWK_jzWrMqxVJ5C8';

  const connectToRoom = async () => {
    try {
      // Configure audio session
      await AudioSession.configureAudio({
        android: {
          preferredOutputList: ['speaker'],
        },
        ios: {
          defaultOutput: 'speaker',
        },
      });

      // Connect to room
      const roomInstance = await connect(LIVEKIT_URL, LIVEKIT_TOKEN, {
        publishDefaults: {
          audioBitrate: 16000,
        },
      });

      setRoom(roomInstance);
      setIsConnected(true);

    } catch (error) {
      console.error('Failed to connect:', error);
    }
  };

  const disconnectFromRoom = async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
      setIsConnected(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>LiveKit Video Call</Text>
      
      <View style={styles.controls}>
        <TouchableOpacity 
          style={[styles.button, isConnected && styles.disabledButton]}
          onPress={connectToRoom}
          disabled={isConnected}
        >
          <Text style={styles.buttonText}>Connect</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, !isConnected && styles.disabledButton]}
          onPress={disconnectFromRoom}
          disabled={!isConnected}
        >
          <Text style={styles.buttonText}>Disconnect</Text>
        </TouchableOpacity>
      </View>

      {isConnected && room && (
        <VideoView 
          style={styles.video}
          room={room}
          participant={room.localParticipant}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 8,
    minWidth: 100,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  video: {
    flex: 1,
    backgroundColor: 'black',
    borderRadius: 8,
  },
});

export default VideoCallScreen;
