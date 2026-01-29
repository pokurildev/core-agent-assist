import React, { useState, useEffect, useCallback } from 'react';
import { adminService } from '@/services/adminService';
import type { Order } from '@/services/adminService';
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
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { RefreshCw, ShoppingCart } from 'lucide-react';
import { toast } from 'sonner';

const Orders: React.FC = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const loadOrders = useCallback(async (quiet = false) => {
        if (!quiet) setLoading(true);
        setIsRefreshing(true);
        try {
            // Updated to fetch real leads
            const data = await adminService.fetchLeads();
            setOrders(data);
        } catch (error) {
            toast.error('Failed to fetch leads');
            console.error(error);
        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        loadOrders();
    }, [loadOrders]);

    // Helpers not needed for basic leads or need update
    // status and date are not in basic lead sheet logic yet

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <ShoppingCart className="h-8 w-8 text-primary" />
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Leads & Orders</h1>
                        <p className="text-muted-foreground">Real-time leads from Google Sheets.</p>
                    </div>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadOrders()}
                    disabled={isRefreshing}
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Recent Leads</CardTitle>
                    <CardDescription>
                        Data sourced from {`Google Sheets (Leads!A:C)`}.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="border rounded-md">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Customer</TableHead>
                                    <TableHead>Phone</TableHead>
                                    <TableHead>Notes</TableHead>
                                    {/* <TableHead>Status</TableHead> */}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={3} className="text-center py-10">
                                            <RefreshCw className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
                                            <p className="mt-2 text-sm text-muted-foreground">Loading leads...</p>
                                        </TableCell>
                                    </TableRow>
                                ) : orders.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={3} className="text-center py-10 text-muted-foreground">
                                            No leads found.
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    orders.map((order, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell className="font-medium">{order.customer_name}</TableCell>
                                            <TableCell className="text-muted-foreground">{order.phone}</TableCell>
                                            <TableCell>{order.notes || "-"}</TableCell>
                                            {/* <TableCell><Badge variant="outline">New</Badge></TableCell> */}
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default Orders;
