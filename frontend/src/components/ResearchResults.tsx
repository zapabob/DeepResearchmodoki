import React from 'react';
import { Box, Typography } from '@mui/material';
import { ResearchResponse } from '../types/research';

interface ResearchResultsProps {
    result: ResearchResponse;
}

const ResearchResults: React.FC<ResearchResultsProps> = ({ result }) => {
    return (
        <Box>
            {result.results.map((item, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                    <Typography variant="h6">{item.title}</Typography>
                    <Typography>{item.snippet || item.content}</Typography>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                        {item.url}
                    </a>
                </Box>
            ))}
            {result.analysis && (
                <Box sx={{ mt: 3 }}>
                    <Typography variant="h6">分析結果</Typography>
                    <Typography>{result.analysis.summary}</Typography>
                </Box>
            )}
        </Box>
    );
};

export default ResearchResults; 