function domcleanupTests(editor)
{
    module("domcleanup tests")
    test("Substitute p for br", function(){
        var r = editor.dataProcessor.toHtml('First line<br/>Second line');
        same(r, 'First line<p />Second line');
    });
    test("Substitute strong for b", function(){
        var r = editor.dataProcessor.toHtml('I am <b>strong</b>');
        same(r, 'I am <strong>strong</strong>');
    });
    test("Multiple br", function(){
        var r = editor.dataProcessor.toHtml('First line<br/><br/>Second line');
        same(r, 'First line<p /><p />Second line');
    });
    test("Drop unwanted elements", function(){
        var r = editor.dataProcessor.toHtml('<style>body{color:red;}</style>');
        same(r, '');
    })
    test("Strip unwanted tags", function(){
        var r = editor.dataProcessor.toHtml('<object>Hello</object>');
        same(r, 'Hello');
    });
    test("Strip unwanted attributes", function(){
        var r = editor.dataProcessor.toHtml('<p style="color:blue;">Hello</p>');
        same(r, '<p>Hello</p>');
    });
}
