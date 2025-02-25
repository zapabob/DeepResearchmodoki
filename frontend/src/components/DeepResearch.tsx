import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Input,
  Stack,
  Text,
  Textarea,
  VStack,
  Heading,
  Card,
  CardBody,
  Badge,
  Flex,
  Spinner,
  useToast,
  FormControl,
  FormLabel,
  Select
} from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';

const MotionCard = motion(Card as any);
const MotionBox = motion(Box as any);
const MotionDiv = motion.div as any;
const MotionFlex = motion(Flex as any);

const CustomVStack = VStack as any;
const CustomStack = Stack as any;

interface ApiResponse {
  query: string;
  timestamp: string;
  results: Array<{
    url: string;
    title: string;
    content: string;
    snippet?: string;
    timestamp: string;
    source?: string;
    analysis?: string;
  }>;
  summary: string;
  additional_findings?: Array<{
    summary: string;
    confidence: number;
  }>;
  metadata: {
    depth: number;
    total_sources: number;
    execution_time: number;
  };
}

export const DeepResearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState(1);
  const [maxPages, setMaxPages] = useState(5);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ApiResponse | null>(null);
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
      const response = await fetch(`${API_URL}/research/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          depth,
          max_pages: maxPages,
          use_cot: false
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API request failed with status ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      setResults(data);
      
      toast({
        title: "検索完了",
        description: `${data.results.length}件の結果が見つかりました`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error during research:', error);
      toast({
        title: "エラーが発生しました",
        description: error instanceof Error ? error.message : "検索中にエラーが発生しました",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return React.createElement(Container, { maxW: "container.xl", py: 8 },
    React.createElement(CustomVStack, { spacing: 8, align: "stretch" }, [
      React.createElement(MotionDiv, {
        style: { textAlign: 'center', marginBottom: '2rem' },
        initial: { opacity: 0, y: -20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.5 },
        key: "header"
      }, [
        React.createElement(Heading, { as: "h1", size: "xl", mb: 2, key: "title" }, "ディープリサーチ"),
        React.createElement(Text, { color: "gray.600", key: "subtitle" }, "AIを活用した高度な検索と仮説検証システム")
      ]),

      React.createElement(MotionCard, {
        variants: fadeIn,
        initial: "initial",
        animate: "animate",
        exit: "exit",
        transition: { duration: 0.3 },
        key: "search-form"
      },
        React.createElement("form", { onSubmit: handleSubmit }, 
          React.createElement(CustomStack, { spacing: 6 }, [
            React.createElement(FormControl, { isRequired: true, key: "query-control" }, [
              React.createElement(FormLabel, { fontSize: "lg", key: "query-label" }, "検索クエリ"),
              React.createElement(Textarea, {
                value: query,
                onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value),
                placeholder: "研究したいトピックや仮説を入力してください",
                size: "lg",
                minH: "150px",
                bg: "white",
                key: "query-input"
              })
            ]),

            React.createElement(Flex, { gap: 4, direction: { base: 'column', md: 'row' }, key: "options" }, [
              React.createElement(FormControl, { flex: 1, key: "depth-control" }, [
                React.createElement(FormLabel, { key: "depth-label" }, "検索深度"),
                React.createElement(Select, {
                  value: depth,
                  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => setDepth(Number(e.target.value)),
                  bg: "white",
                  key: "depth-select"
                }, [
                  React.createElement("option", { value: 1, key: "depth-1" }, "標準"),
                  React.createElement("option", { value: 2, key: "depth-2" }, "詳細"),
                  React.createElement("option", { value: 3, key: "depth-3" }, "網羅的")
                ])
              ]),

              React.createElement(FormControl, { flex: 1, key: "pages-control" }, [
                React.createElement(FormLabel, { key: "pages-label" }, "最大ページ数"),
                React.createElement(Input, {
                  type: "number",
                  value: maxPages,
                  onChange: (e: React.ChangeEvent<HTMLInputElement>) => setMaxPages(Number(e.target.value)),
                  min: 1,
                  max: 20,
                  bg: "white",
                  key: "pages-input"
                })
              ])
            ]),

            React.createElement(Button, {
              type: "submit",
              size: "lg",
              isLoading: loading,
              loadingText: "検索中...",
              w: "full",
              key: "submit-button"
            }, "深層検索を開始")
          ])
        )
      ),

      loading && React.createElement(AnimatePresence, { key: "loading-animation" },
        React.createElement(MotionFlex, {
          initial: { opacity: 0 },
          animate: { opacity: 1 },
          exit: { opacity: 0 },
          style: {
            justifyContent: 'center',
            alignItems: 'center',
            padding: '2rem 0'
          },
          key: "loading-flex"
        },
          React.createElement(motion.div, {
            animate: {
              scale: [1, 1.2, 1],
              rotate: [0, 180, 360],
            },
            transition: {
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            },
            key: "spinner-container"
          },
            React.createElement(Spinner, { size: "xl", key: "spinner" })
          )
        )
      ),

      results && React.createElement(AnimatePresence, { key: "results-animation" },
        React.createElement(motion.div, {
          variants: staggerChildren,
          initial: "initial",
          animate: "animate",
          exit: "exit",
          key: "results-container"
        },
          React.createElement(CustomVStack, { spacing: 6, align: "stretch" }, [
            React.createElement(MotionCard, { variants: fadeIn, key: "summary-card" },
              React.createElement(CardBody, {}, [
                React.createElement(Heading, { size: "md", mb: 4, key: "summary-heading" }, "検索結果の要約"),
                React.createElement(Text, { whiteSpace: "pre-wrap", key: "summary-text" }, results.summary)
              ])
            ),

            React.createElement(MotionCard, { variants: fadeIn, key: "results-card" },
              React.createElement(CardBody, {}, [
                React.createElement(Heading, { size: "md", mb: 4, key: "results-heading" }, 
                  `検索結果 (${results.results.length}件)`
                ),
                React.createElement(CustomStack, { spacing: 4, key: "results-stack" }, 
                  results.results.map((result, index) => 
                    React.createElement(MotionBox, {
                      key: index,
                      variants: fadeIn,
                      style: {
                        padding: '1rem',
                        borderWidth: '1px',
                        borderRadius: '0.5rem',
                        backgroundColor: 'white',
                        boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                      },
                      whileHover: { scale: 1.02 },
                      whileTap: { scale: 0.98 }
                    }, [
                      React.createElement(Heading, { size: "sm", mb: 2, key: `title-${index}` }, result.title),
                      React.createElement(Text, {
                        color: "blue.600",
                        mb: 2,
                        fontSize: "sm",
                        wordBreak: "break-all",
                        key: `url-${index}`
                      }, 
                        React.createElement("a", {
                          href: result.url,
                          target: "_blank",
                          rel: "noopener noreferrer",
                          key: `link-${index}`
                        }, result.url)
                      ),
                      React.createElement(Text, { mb: 2, fontSize: "sm", key: `snippet-${index}` }, result.snippet),
                      result.analysis && React.createElement(Box, { 
                        mt: 2, 
                        bg: "gray.50", 
                        p: 3, 
                        borderRadius: "md",
                        key: `analysis-box-${index}`
                      }, [
                        React.createElement(Text, { 
                          fontWeight: "bold", 
                          fontSize: "sm", 
                          mb: 2,
                          key: `analysis-title-${index}`
                        }, "Chain of Thought 分析:"),
                        React.createElement(Text, { 
                          fontSize: "sm", 
                          whiteSpace: "pre-wrap",
                          key: `analysis-text-${index}`
                        }, result.analysis)
                      ])
                    ])
                  )
                )
              ])
            ),

            results.additional_findings && results.additional_findings.length > 0 && 
              React.createElement(MotionCard, { variants: fadeIn, key: "findings-card" },
                React.createElement(CardBody, {}, [
                  React.createElement(Heading, { size: "md", mb: 4, key: "findings-heading" }, "追加の発見"),
                  React.createElement(CustomStack, { spacing: 4, key: "findings-stack" }, 
                    results.additional_findings.map((finding, index) => 
                      React.createElement(MotionBox, {
                        key: index,
                        variants: fadeIn,
                        style: {
                          padding: '1rem',
                          borderWidth: '1px',
                          borderRadius: '0.5rem',
                          backgroundColor: 'white',
                          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                        },
                        whileHover: { scale: 1.02 },
                        whileTap: { scale: 0.98 }
                      }, [
                        React.createElement(Text, { 
                          whiteSpace: "pre-wrap",
                          key: `finding-text-${index}`
                        }, finding.summary),
                        React.createElement(Badge, { 
                          colorScheme: "green", 
                          mt: 2,
                          key: `finding-badge-${index}`
                        }, `信頼度: ${Math.round(finding.confidence * 100)}%`)
                      ])
                    )
                  )
                ])
              ),

            React.createElement(MotionCard, { variants: fadeIn, key: "metadata-card" },
              React.createElement(CardBody, {}, [
                React.createElement(Heading, { size: "md", mb: 4, key: "metadata-heading" }, "メタデータ"),
                React.createElement(CustomStack, { spacing: 2, key: "metadata-stack" }, [
                  React.createElement(MotionFlex, {
                    style: {
                      alignItems: 'center',
                      gap: '0.5rem'
                    },
                    whileHover: { x: 10 },
                    transition: { duration: 0.2 },
                    key: "depth-flex"
                  }, [
                    React.createElement(Badge, { colorScheme: "blue", key: "depth-badge" }, "検索深度"),
                    React.createElement(Text, { key: "depth-value" }, results.metadata.depth)
                  ]),
                  React.createElement(MotionFlex, {
                    style: {
                      alignItems: 'center',
                      gap: '0.5rem'
                    },
                    whileHover: { x: 10 },
                    transition: { duration: 0.2 },
                    key: "sources-flex"
                  }, [
                    React.createElement(Badge, { colorScheme: "green", key: "sources-badge" }, "ソース数"),
                    React.createElement(Text, { key: "sources-value" }, results.metadata.total_sources)
                  ]),
                  React.createElement(MotionFlex, {
                    style: {
                      alignItems: 'center',
                      gap: '0.5rem'
                    },
                    whileHover: { x: 10 },
                    transition: { duration: 0.2 },
                    key: "time-flex"
                  }, [
                    React.createElement(Badge, { colorScheme: "purple", key: "time-badge" }, "実行時間"),
                    React.createElement(Text, { key: "time-value" }, `${results.metadata.execution_time}ms`)
                  ])
                ])
              ])
            )
          ])
        )
      )
    ])
  );
}; 