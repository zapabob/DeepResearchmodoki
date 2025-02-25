import React, { useState } from 'react';
import { ChakraProvider, Box, Container, Heading, Text, VStack, Input, Button, Spinner, useToast } from '@chakra-ui/react';
import { researchApi } from './services/api';
import { ResearchRequest } from './types/research';
import ResultsDisplay from './components/ResultsDisplay';
import Header from './components/Header';
import Footer from './components/Footer';
import ApiHealthCheck from './components/ApiHealthCheck';

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: '検索クエリを入力してください',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const request: ResearchRequest = {
        query: query,
        max_pages: 5,
        language: 'ja'
      };

      const response = await researchApi.conductResearch(request);
      setResults(response);
      
      toast({
        title: '検索完了',
        description: `${response.results.length}件の結果が見つかりました`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Search error:', err);
      setError('検索中にエラーが発生しました。もう一度お試しください。');
      
      toast({
        title: 'エラーが発生しました',
        description: '検索中にエラーが発生しました。もう一度お試しください。',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return React.createElement(
    ChakraProvider,
    null,
    React.createElement(
      Box,
      { minH: "100vh", display: "flex", flexDirection: "column" },
      React.createElement(Header, null),
      React.createElement(
        Container,
        { maxW: "container.xl", flex: "1", py: 8 },
        React.createElement(
          VStack,
          { spacing: 8, align: "stretch" },
          React.createElement(
            Box,
            { textAlign: "center", py: 10 },
            React.createElement(Heading, { as: "h1", size: "2xl", mb: 4 }, "Web Deep Research"),
            React.createElement(
              Text,
              { fontSize: "xl", mb: 6 },
              "ウェブ全体の詳細検索とChain-of-Thought（CoT）による仮説検証思考"
            ),
            React.createElement(
              Box,
              { display: "flex", maxW: "600px", mx: "auto" },
              React.createElement(Input, {
                placeholder: "検索クエリを入力してください",
                size: "lg",
                value: query,
                onChange: (e) => setQuery(e.target.value),
                onKeyPress: handleKeyPress,
                mr: 4
              }),
              React.createElement(
                Button,
                {
                  colorScheme: "blue",
                  size: "lg",
                  onClick: handleSearch,
                  isLoading: isLoading,
                  loadingText: "検索中"
                },
                "検索"
              )
            ),
            React.createElement(
              Box,
              { mt: 4 },
              React.createElement(ApiHealthCheck, null)
            )
          ),
          isLoading && React.createElement(
            Box,
            { textAlign: "center", py: 10 },
            React.createElement(Spinner, { size: "xl" }),
            React.createElement(Text, { mt: 4 }, "検索中です。しばらくお待ちください...")
          ),
          error && React.createElement(
            Box,
            { bg: "red.50", p: 4, borderRadius: "md" },
            React.createElement(Text, { color: "red.500" }, error)
          ),
          results && React.createElement(ResultsDisplay, { results: results })
        )
      ),
      React.createElement(Footer, null)
    )
  );
}

export default App; 