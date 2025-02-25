import React from 'react';
import { Box, Text, Flex, Link } from '@chakra-ui/react';

const Footer: React.FC = () => {
  return React.createElement(
    Box,
    { as: "footer", bg: "gray.100", py: 6, px: 8 },
    React.createElement(
      Flex,
      {
        direction: { base: 'column', md: 'row' },
        justify: "space-between",
        align: "center",
        maxW: "container.xl",
        mx: "auto"
      },
      React.createElement(
        Text,
        { fontSize: "sm", color: "gray.600" },
        `© ${new Date().getFullYear()} Web Deep Research. All rights reserved.`
      ),
      React.createElement(
        Flex,
        { mt: { base: 4, md: 0 } },
        React.createElement(
          Link,
          { href: "#", mx: 2, fontSize: "sm", color: "gray.600" },
          "プライバシーポリシー"
        ),
        React.createElement(
          Link,
          { href: "#", mx: 2, fontSize: "sm", color: "gray.600" },
          "利用規約"
        ),
        React.createElement(
          Link,
          { href: "#", mx: 2, fontSize: "sm", color: "gray.600" },
          "お問い合わせ"
        )
      )
    )
  );
};

export default Footer; 