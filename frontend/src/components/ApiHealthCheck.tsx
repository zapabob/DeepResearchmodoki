import React, { useEffect, useState } from 'react';
import { Box, Text, Badge, Spinner } from '@chakra-ui/react';
import { researchApi } from '../services/api';

const ApiHealthCheck: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading');
  const [message, setMessage] = useState<string>('APIサーバーの状態を確認中...');

  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const response = await researchApi.checkHealth();
        if (response.status === 'ok') {
          setStatus('online');
          setMessage('APIサーバーはオンラインです');
        } else {
          setStatus('offline');
          setMessage('APIサーバーは応答していますが、正常ではありません');
        }
      } catch (error) {
        console.error('API health check failed:', error);
        setStatus('offline');
        setMessage('APIサーバーに接続できません');
      }
    };

    checkApiHealth();
  }, []);

  return React.createElement(
    Box,
    { p: 3, borderWidth: "1px", borderRadius: "md", display: "inline-flex", alignItems: "center" },
    status === 'loading' && React.createElement(Spinner, { size: "sm", mr: 2 }),
    status === 'online' && React.createElement(Badge, { colorScheme: "green", mr: 2 }, "オンライン"),
    status === 'offline' && React.createElement(Badge, { colorScheme: "red", mr: 2 }, "オフライン"),
    React.createElement(Text, { fontSize: "sm" }, message)
  );
};

export default ApiHealthCheck; 