$(function(){  
    var number_form_opens = 0;
    var last_open = 0;
    
    $('a.reply_to_comment').hide();
    
    $('a.reply_to_comment').click(function() {
        id_comment = $(this).attr('id');
        id_comment = id_comment.split('to_comment_')[1];
        
        if (last_open == id_comment) {
            $('#fast_reply_to_'+id_comment).remove();
            last_open = 0;
            return false;
        }
        
        if (number_form_opens > 0)
            $('._list_form_opens').remove();

        $('input#id_parent').val(id_comment);
        $('._content_form_comments').clone(true).insertBefore('#show_form_'+id_comment);
        $('#c'+id_comment).find('._content_form_comments').attr('id', 'fast_reply_to_'+id_comment);
        
        $('#fast_reply_to_'+id_comment).addClass('_list_form_opens').prepend('<p><a href="#" class="cancel_fast_reply" id="cancel_'+id_comment+'">Cliquez ici pour annuler votre réponse</a></p>');
        
        number_form_opens += 1;
        last_open = id_comment;
        
        $('a.cancel_fast_reply').click(function() {
            id_comment = $(this).attr('id');
            id_comment = id_comment.split('cancel_')[1];
            $('#fast_reply_to_'+id_comment).remove();
            $('input#id_parent').empty();
            number_form_opens -= 1;
            last_open = 0;
            return false;
        });
        return false;
    });
    
    $('.row_comment').mouseover(function() {
        $(this).find('a.reply_to_comment').show();
    }).mouseout(function() {
        $(this).find('a.reply_to_comment').hide();
    });
});