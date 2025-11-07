// Inisialisasi
        document.addEventListener('DOMContentLoaded', function() {
            initializeApp();
            setupEventListeners();
            loadInitialData();
        });

        async function initializeApp() {
            // Set tanggal default ke hari ini
            document.getElementById('transactionDate').valueAsDate = new Date();
            
            // Set default type to income
            setTransactionType('income');
        }

        function setupEventListeners() {
            // Toggle jenis transaksi
            document.getElementById('btnIncome').addEventListener('click', () => setTransactionType('income'));
            document.getElementById('btnExpense').addEventListener('click', () => setTransactionType('expense'));
            
            // Form submission
            document.getElementById('transactionForm').addEventListener('submit', handleFormSubmit);
        }

        async function loadInitialData() {
            await loadTransactions();
            await loadFinancialSummary();
        }

        function setTransactionType(type) {
            document.getElementById('transactionType').value = type;
            
            // Update UI
            const incomeBtn = document.getElementById('btnIncome');
            const expenseBtn = document.getElementById('btnExpense');
            
            if (type === 'income') {
                incomeBtn.classList.add('active');
                expenseBtn.classList.remove('active');
            } else {
                expenseBtn.classList.add('active');
                incomeBtn.classList.remove('active');
            }
        }

        async function handleFormSubmit(e) {
            e.preventDefault();
            
            const form = document.getElementById('transactionForm');
            
            // Show loading state
            form.classList.add('loading');
            
            const transactionData = {
                title: document.getElementById('transactionTitle').value,
                amount: parseFloat(document.getElementById('transactionAmount').value),
                type: document.getElementById('transactionType').value,
                category: document.getElementById('transactionCategory').value,
                transaction_date: document.getElementById('transactionDate').value,
                notes: document.getElementById('transactionNotes').value
            };
            
            try {
                const result = await eel.add_transaction(
                    transactionData.title,
                    transactionData.amount,
                    transactionData.type,
                    transactionData.category,
                    transactionData.transaction_date,
                    transactionData.notes
                )();
                
                if (result.status === 'success') {
                    showNotification(result.message, 'success');
                    await loadTransactions();
                    await loadFinancialSummary();
                    form.reset();
                    document.getElementById('transactionDate').valueAsDate = new Date();
                    setTransactionType('income');
                } else {
                    showNotification(result.message, 'error');
                }
            } catch (error) {
                showNotification('Terjadi kesalahan saat menyimpan transaksi', 'error');
                console.error('Error:', error);
            } finally {
                form.classList.remove('loading');
            }
        }

        async function deleteTransaction(id) {
            if (confirm('Apakah Anda yakin ingin menghapus transaksi ini?')) {
                try {
                    const result = await eel.delete_transaction(id)();
                    if (result.status === 'success') {
                        showNotification(result.message, 'success');
                        await loadTransactions();
                        await loadFinancialSummary();
                    } else {
                        showNotification(result.message, 'error');
                    }
                } catch (error) {
                    showNotification('Terjadi kesalahan saat menghapus transaksi', 'error');
                    console.error('Error:', error);
                }
            }
        }

        async function loadFinancialSummary() {
            try {
                const result = await eel.get_financial_summary()();
                if (result.status === 'success') {
                    const data = result.data;
                    document.getElementById('totalIncome').textContent = formatCurrency(data.total_income);
                    document.getElementById('totalExpense').textContent = formatCurrency(data.total_expense);
                    document.getElementById('totalBalance').textContent = formatCurrency(data.balance);
                }
            } catch (error) {
                console.error('Error loading financial summary:', error);
            }
        }

        async function loadTransactions() {
            try {
                const result = await eel.get_all_transactions()();
                displayTransactions(result);
            } catch (error) {
                showNotification('Terjadi kesalahan saat memuat transaksi', 'error');
                console.error('Error:', error);
            }
        }

        function displayTransactions(result) {
            const transactionsList = document.getElementById('transactionsList');
            
            if (result.status !== 'success' || !result.data || result.data.length === 0) {
                transactionsList.innerHTML = `
                    <div class="no-transactions">
                        <i class="fas fa-receipt" style="font-size: 2.5em; margin-bottom: 10px; opacity: 0.5;"></i>
                        <p>Belum ada transaksi</p>
                    </div>
                `;
                return;
            }
            
            const transactions = result.data;
            
            transactionsList.innerHTML = transactions.map(transaction => `
                <div class="transaction-item transaction-${transaction.type}">
                    <div class="transaction-info">
                        <div class="transaction-title">${transaction.title}</div>
                        <div class="transaction-category">
                            ${transaction.category} • ${formatDate(transaction.transaction_date)}
                        </div>
                        ${transaction.notes ? `<div class="transaction-date">${transaction.notes}</div>` : ''}
                    </div>
                    <div class="transaction-amount">
                        ${transaction.type === 'income' ? '+' : '-'} ${formatCurrency(transaction.amount)}
                    </div>
                    <div class="transaction-actions">
                        <button class="btn-icon btn-delete" onclick="deleteTransaction(${transaction.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function formatCurrency(amount) {
            return new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                minimumFractionDigits: 0
            }).format(amount);
        }

        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('id-ID', {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            });
        }

        function showNotification(message, type) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type}`;
            
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }