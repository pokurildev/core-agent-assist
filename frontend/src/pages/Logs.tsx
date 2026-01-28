import React, { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw, ScrollText } from 'lucide-react';
import { toast } from 'sonner';

interface LogEntry {
    timestamp: string;
    level: string;
    message: string;
    module: string;
    function: string;
    line: number;
}

const Logs: React.FC = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const loadLogs = useCallback(async (quiet = false) => {
        if (!quiet) setIsRefreshing(true);
        try {
            const data = await adminService.fetchLogs();
            // Сортируем: новые сверху
            const sortedLogs = [...data].reverse();
            setLogs(sortedLogs);
        } catch (error) {
            if (!quiet) toast.error('Failed to fetch logs');
            console.error(error);
        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        loadLogs();
        const interval = setInterval(() => {
            loadLogs(true);
        }, 5000);
        return () => clearInterval(interval);
    }, [loadLogs]);

    const getLevelBadge = (level?: string) => {
        if (!level) return <Badge variant="outline">LOG</Badge>;
        switch (level.toUpperCase()) {
            case 'ERROR':
                return <Badge variant="destructive">ERROR</Badge>;
            case 'WARNING':
                return <Badge className="bg-yellow-500 hover:bg-yellow-600 text-white">WARNING</Badge>;
            case 'INFO':
                return <Badge variant="secondary">INFO</Badge>;
            case 'DEBUG':
                return <Badge variant="outline">DEBUG</Badge>;
            default:
                return <Badge>{level}</Badge>;
        }
    };

    const formatTimestamp = (ts: string) => {
        try {
            return new Date(ts).toLocaleString();
        } catch {
            return ts;
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <ScrollText className="h-8 w-8 text-primary" />
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">System Logs</h1>
                        <p className="text-muted-foreground">Real-time server logs from the Omnicore AI Backend.</p>
                    </div>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadLogs()}
                    disabled={isRefreshing}
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            <div className="border rounded-lg bg-card shadow-sm">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[180px]">Timestamp</TableHead>
                            <TableHead className="w-[100px]">Level</TableHead>
                            <TableHead>Message</TableHead>
                            <TableHead className="w-[150px]">Location</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={4} className="text-center py-10">
                                    <RefreshCw className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
                                    <p className="mt-2 text-sm text-muted-foreground">Loading initial logs...</p>
                                </TableCell>
                            </TableRow>
                        ) : logs.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} className="text-center py-10 text-muted-foreground">
                                    No logs found or file is empty.
                                </TableCell>
                            </TableRow>
                        ) : (
                            logs.map((log, idx) => (
                                <TableRow key={idx} className="font-mono text-xs">
                                    <TableCell className="text-muted-foreground">
                                        {formatTimestamp(log.timestamp)}
                                    </TableCell>
                                    <TableCell>
                                        {getLevelBadge(log.level)}
                                    </TableCell>
                                    <TableCell className="max-w-md truncate md:max-w-xl">
                                        <span title={log.message}>{log.message}</span>
                                    </TableCell>
                                    <TableCell className="text-muted-foreground truncate">
                                        <span title={`${log.module}.${log.function}:${log.line}`}>
                                            {log.module}:{log.line}
                                        </span>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
            <p className="text-[10px] text-muted-foreground text-center">
                Showing last 50 log entries. Auto-refreshing every 5s.
            </p>
        </div>
    );
};

export default Logs;
