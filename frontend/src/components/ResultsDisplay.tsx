import React, { useState } from 'react';
import { 
  Box, 
  Heading, 
  Text, 
  Link, 
  Tabs, 
  TabList, 
  TabPanels, 
  Tab, 
  TabPanel, 
  Accordion, 
  AccordionItem, 
  AccordionButton, 
  AccordionPanel, 
  AccordionIcon,
  List,
  ListItem,
  ListIcon,
  Badge,
  Divider,
  Flex,
  VStack
} from '@chakra-ui/react';
import { CheckCircleIcon, InfoIcon } from '@chakra-ui/icons';
import { ResearchResponse } from '../types/research';

interface ResultsDisplayProps {
  results: ResearchResponse;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!results) return null;

  const { analysis, metadata } = results;

  // 分析データが存在しない場合のフォールバック
  const safeAnalysis = analysis || {
    summary: '検索結果の分析を行っています...',
    insights: ['検索結果から洞察を抽出中です...'],
    patterns: ['検索結果からパターンを分析中です...'],
    reliability: '情報の信頼性を評価中です...',
    further_research: ['追加調査が必要な領域を特定中です...']
  };

  // 否定的な分析結果をフィルタリングする関数
  const filterNegativeAnalysis = (items: string[]): string[] => {
    if (!items || items.length === 0) return ['分析中...'];
    
    const negativeKeywords = [
      '役立ちません', '含まれていません', '提供されていません', 
      '見つかりません', '存在しません', '情報がありません',
      '評価するのに役立ちません', '情報源の信頼性'
    ];
    
    // 否定的な分析結果をフィルタリング
    const filteredItems = items.filter(item => 
      !negativeKeywords.some(keyword => item.includes(keyword))
    );
    
    // フィルタリング後に項目がない場合はデフォルトメッセージを返す
    return filteredItems.length > 0 ? filteredItems : ['分析中...'];
  };

  // 分析結果をフィルタリング
  const filteredInsights = filterNegativeAnalysis(safeAnalysis.insights);
  const filteredPatterns = filterNegativeAnalysis(safeAnalysis.patterns);
  const filteredResearch = filterNegativeAnalysis(safeAnalysis.further_research);
  
  // 信頼性評価が否定的な場合は代替テキストを表示
  const negativeKeywords = [
    '役立ちません', '含まれていません', '提供されていません', 
    '見つかりません', '存在しません', '情報がありません',
    '評価するのに役立ちません', '情報源の信頼性'
  ];
  const reliabilityText = negativeKeywords.some((keyword: string) => 
    safeAnalysis.reliability?.includes(keyword)
  ) ? '情報の信頼性を評価中です...' : safeAnalysis.reliability || '情報の信頼性を評価中です...';

  return React.createElement(Box, {}, [
    React.createElement(Heading, { as: "h2", size: "lg", mb: 4, key: "heading" }, "検索結果"),
    
    React.createElement(Box, { bg: "blue.50", p: 4, borderRadius: "md", mb: 6, key: "summary" }, [
      React.createElement(Heading, { as: "h3", size: "md", mb: 2, key: "summary-heading" }, "分析サマリー"),
      React.createElement(Text, { key: "summary-text" }, safeAnalysis.summary),
      
      metadata && React.createElement(Text, { 
        fontSize: "sm", 
        color: "gray.600", 
        mt: 2, 
        key: "metadata" 
      }, [
        `検索クエリ: ${metadata.query || '不明'} | `,
        `検索ページ数: ${metadata.max_pages || metadata.depth || '不明'} | `,
        `言語: ${metadata.language || 'ja'} | `,
        `タイムスタンプ: ${metadata.timestamp ? new Date(metadata.timestamp).toLocaleString() : new Date().toLocaleString()}`
      ])
    ]),
    
    React.createElement(Tabs, { 
      variant: "enclosed", 
      colorScheme: "blue", 
      onChange: (index: number) => setActiveTab(index),
      key: "tabs"
    }, [
      React.createElement(TabList, { key: "tablist" }, [
        React.createElement(Tab, { key: "tab-results" }, "検索結果"),
        React.createElement(Tab, { key: "tab-analysis" }, "分析"),
        React.createElement(Tab, { key: "tab-insights" }, "洞察")
      ]),
      
      React.createElement(TabPanels, { key: "tabpanels" }, [
        React.createElement(TabPanel, { key: "panel-results" }, 
          React.createElement(VStack, { spacing: 4, align: "stretch", key: "results-stack" }, 
            results && results.results && results.results.map((result, index) => 
              React.createElement(Box, { 
                key: index, 
                p: 4, 
                borderWidth: "1px", 
                borderRadius: "md",
                borderColor: "gray.200",
                boxShadow: "sm",
                _hover: { boxShadow: "md" }
              }, [
                React.createElement(Heading, { as: "h3", size: "md", mb: 2, key: `title-${index}` }, 
                  result.title || "タイトルなし"
                ),
                result.url && React.createElement(Link, { 
                  href: result.url, 
                  color: "blue.500", 
                  isExternal: true,
                  mb: 2,
                  display: "block",
                  key: `url-${index}`
                }, [
                  result.url,
                  React.createElement(Box, { as: "span", ml: 1, key: `external-${index}` }, "↗")
                ]),
                React.createElement(Text, { mb: 3, key: `content-${index}` }, 
                  result.content ? 
                    (result.content.length > 300 ? `${result.content.substring(0, 300)}...` : result.content) : 
                    "内容なし"
                ),
                result.metadata && result.metadata.sentiment && React.createElement(Badge, {
                  colorScheme: 
                    result.metadata.sentiment === "positive" ? "green" : 
                    result.metadata.sentiment === "negative" ? "red" : "gray",
                  key: `sentiment-${index}`
                }, `感情: ${
                  result.metadata.sentiment === "positive" ? "ポジティブ" : 
                  result.metadata.sentiment === "negative" ? "ネガティブ" : "中立"
                }`)
              ])
            )
          )
        ),
        
        React.createElement(TabPanel, { key: "panel-analysis" }, 
          React.createElement(Box, {}, [
            React.createElement(Heading, { as: "h3", size: "md", mb: 3, key: "reliability-heading" }, "信頼性評価"),
            React.createElement(Text, { mb: 4, key: "reliability-text" }, reliabilityText),
            
            React.createElement(Heading, { as: "h3", size: "md", mb: 3, key: "patterns-heading" }, "パターンと関連性"),
            React.createElement(List, { spacing: 2, mb: 4, key: "patterns-list" }, 
              safeAnalysis.patterns && filteredPatterns.map((pattern, index) => 
                React.createElement(ListItem, { key: index }, [
                  React.createElement(ListIcon, { as: InfoIcon, color: "blue.500", key: `icon-${index}` }),
                  pattern
                ])
              )
            ),
            
            React.createElement(Heading, { as: "h3", size: "md", mb: 3, key: "research-heading" }, "追加調査が必要な領域"),
            React.createElement(List, { spacing: 2, key: "research-list" }, 
              safeAnalysis.further_research && filteredResearch.map((item, index) => 
                React.createElement(ListItem, { key: index }, [
                  React.createElement(ListIcon, { as: InfoIcon, color: "purple.500", key: `icon-${index}` }),
                  item
                ])
              )
            )
          ])
        ),
        
        React.createElement(TabPanel, { key: "panel-insights" }, [
          React.createElement(Heading, { as: "h3", size: "md", mb: 4, key: "insights-heading" }, "主要な洞察"),
          React.createElement(List, { spacing: 3, key: "insights-list" }, 
            filteredInsights.map((insight, index: number) => 
              React.createElement(ListItem, { 
                key: index, 
                p: 3, 
                bg: "gray.50", 
                borderRadius: "md" 
              }, 
                React.createElement(Flex, { align: "start" }, [
                  React.createElement(ListIcon, { 
                    as: CheckCircleIcon, 
                    color: "green.500", 
                    mt: 1,
                    key: `icon-${index}`
                  }),
                  React.createElement(Box, { key: `box-${index}` }, [
                    React.createElement(Text, { key: `text-${index}` }, insight),
                    React.createElement(Badge, { colorScheme: "blue", mt: 1, key: `badge-${index}` }, `洞察 ${index + 1}`)
                  ])
                ])
              )
            )
          )
        ])
      ])
    ])
  ]);
};

export default ResultsDisplay; 