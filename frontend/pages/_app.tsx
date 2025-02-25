import React from 'react';
import type { AppProps } from 'next/app';
import { ChakraProvider } from '@chakra-ui/react';
import '../src/index.css';

function MyApp({ Component, pageProps }: AppProps) {
  return React.createElement(
    ChakraProvider,
    null,
    React.createElement(Component, pageProps)
  );
}

export default MyApp; 