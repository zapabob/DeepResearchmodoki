import React from 'react';
import { Box, Flex, Heading, Button, useColorMode, IconButton } from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';

const Header: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return React.createElement(
    Box,
    { as: "header", bg: "blue.600", color: "white", py: 4, px: 8, boxShadow: "md" },
    React.createElement(
      Flex,
      { justify: "space-between", align: "center", maxW: "container.xl", mx: "auto" },
      React.createElement(Heading, { as: "h1", size: "lg" }, "Web Deep Research"),
      React.createElement(
        Flex,
        { align: "center" },
        React.createElement(
          Button,
          { variant: "ghost", mr: 4, _hover: { bg: "blue.500" } },
          "ホーム"
        ),
        React.createElement(
          Button,
          { variant: "ghost", mr: 4, _hover: { bg: "blue.500" } },
          "履歴"
        ),
        React.createElement(
          Button,
          { variant: "ghost", mr: 4, _hover: { bg: "blue.500" } },
          "ヘルプ"
        ),
        React.createElement(
          IconButton,
          {
            "aria-label": "ダークモード切替",
            icon: colorMode === 'light' ? React.createElement(MoonIcon, null) : React.createElement(SunIcon, null),
            onClick: toggleColorMode,
            variant: "ghost",
            _hover: { bg: "blue.500" }
          }
        )
      )
    )
  );
};

export default Header; 