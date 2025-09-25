// JavaScript customizado para o Sistema de Upload CSV

$(document).ready(function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts após 5 segundos
    $('.alert').each(function() {
        var alert = $(this);
        if (!alert.hasClass('alert-danger')) {
            setTimeout(function() {
                alert.fadeOut();
            }, 5000);
        }
    });

    // Validação de formulários
    $('form').on('submit', function(e) {
        var form = $(this);
        var submitBtn = form.find('button[type="submit"]');
        
        // Desabilitar botão de submit para evitar duplo envio
        submitBtn.prop('disabled', true);
        
        // Reabilitar após 3 segundos (caso haja erro)
        setTimeout(function() {
            submitBtn.prop('disabled', false);
        }, 3000);
    });

    // Validação de confirmação de senha
    $('#confirm_password, #confirm_email').on('input', function() {
        var field = $(this);
        var originalField = field.attr('id') === 'confirm_password' ? $('#password') : $('#email');
        
        if (field.val() !== originalField.val()) {
            field[0].setCustomValidity('Os valores não coincidem');
        } else {
            field[0].setCustomValidity('');
        }
    });

    // Drag and drop para upload de arquivos
    var uploadArea = $('.upload-area');
    if (uploadArea.length) {
        uploadArea.on('dragover', function(e) {
            e.preventDefault();
            $(this).addClass('dragover');
        });

        uploadArea.on('dragleave', function(e) {
            e.preventDefault();
            $(this).removeClass('dragover');
        });

        uploadArea.on('drop', function(e) {
            e.preventDefault();
            $(this).removeClass('dragover');
            
            var files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                $('#file')[0].files = files;
                updateFileInfo(files[0]);
            }
        });

        uploadArea.on('click', function() {
            $('#file').click();
        });
    }

    // Atualizar informações do arquivo selecionado
    $('#file').on('change', function() {
        var file = this.files[0];
        if (file) {
            updateFileInfo(file);
        }
    });

    // Função para atualizar informações do arquivo
    function updateFileInfo(file) {
        var fileInfo = $('.file-info');
        if (fileInfo.length === 0) {
            fileInfo = $('<div class="file-info mt-2"></div>');
            $('#file').after(fileInfo);
        }
        
        var size = formatFileSize(file.size);
        var html = '<div class="alert alert-info">' +
                   '<i class="bi bi-file-earmark-spreadsheet"></i> ' +
                   '<strong>' + file.name + '</strong> (' + size + ')' +
                   '</div>';
        
        fileInfo.html(html);
    }

    // Função para formatar tamanho do arquivo
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        var k = 1024;
        var sizes = ['Bytes', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Confirmação para ações perigosas
    $('.btn-danger, .btn-outline-danger').on('click', function(e) {
        var action = $(this).text().trim();
        if (action.includes('Excluir') || action.includes('Delete')) {
            if (!confirm('Tem certeza que deseja realizar esta ação? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        }
    });

    // Atualizar estatísticas em tempo real (se necessário)
    if (typeof updateStats === 'function') {
        setInterval(updateStats, 30000); // Atualizar a cada 30 segundos
    }

    // Inicializar DataTables com configurações padrão
    if ($.fn.DataTable) {
        $('.data-table').DataTable({
            "language": {
                "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json"
            },
            "pageLength": 25,
            "responsive": true,
            "order": [[ 0, "desc" ]],
            "columnDefs": [
                { "orderable": false, "targets": -1 } // Desabilitar ordenação na última coluna
            ]
        });
    }

    // Smooth scroll para links internos
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 70
            }, 500);
        }
    });

    // Adicionar classe de animação aos elementos
    $('.card, .alert').addClass('fade-in');
});

// Funções globais
window.formatBytes = function(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    var k = 1024;
    var sizes = ['Bytes', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Função para mostrar loading
window.showLoading = function(element) {
    var btn = $(element);
    var originalText = btn.html();
    btn.html('<span class="spinner-border spinner-border-sm me-2"></span>Carregando...');
    btn.prop('disabled', true);
    
    return function() {
        btn.html(originalText);
        btn.prop('disabled', false);
    };
};

// Função para copiar texto para clipboard
window.copyToClipboard = function(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copiado para a área de transferência!', 'success');
        });
    } else {
        // Fallback para navegadores mais antigos
        var textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copiado para a área de transferência!', 'success');
    }
};

// Função para mostrar toast (notificação)
window.showToast = function(message, type) {
    type = type || 'info';
    var alertClass = 'alert-' + type;
    
    var toast = $('<div class="alert ' + alertClass + ' alert-dismissible fade show position-fixed" ' +
                  'style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">' +
                  '<i class="bi bi-info-circle"></i> ' + message +
                  '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                  '</div>');
    
    $('body').append(toast);
    
    setTimeout(function() {
        toast.alert('close');
    }, 5000);
};

// Função para validar email
window.isValidEmail = function(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

// Função para validar arquivo CSV
window.isValidCSV = function(file) {
    return file && file.type === 'text/csv' && file.name.toLowerCase().endsWith('.csv');
};
