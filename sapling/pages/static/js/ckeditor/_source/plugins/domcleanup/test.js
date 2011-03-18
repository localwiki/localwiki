function domcleanupTests(editor)
{
    module("domcleanup tests")
    test("Substitute p for br", function(){
        editor.setData('First line<br/>Second line');
        same(editor.getData(),
            '<p>\n\tFirst line</p>\n<p>\n\tSecond line</p>\n');
    });
    test("Substitute strong for b", function(){
        editor.setData('I am <b>strong</b>');
        same(editor.getData(),
            '<p>\n\tI am <strong>strong</strong></p>\n');
    });
    test("Multiple br", function(){
        editor.setData('First line<br/><br/>Second line');
        same(editor.getData(),
            '<p>\n\tFirst line</p>\n<p>\n\t&nbsp;</p>\n<p>\n\tSecond line</p>\n');
    });
    test("Drop unwanted elements", function(){
        editor.setData('<style>body { color: red; }</style>');
        same(editor.getData(), '');
    })
    test("Strip unwanted tags", function(){
        editor.setData('<div>Hello</div>');
        same(editor.getData(),
            '<p>\n\tHello</p>\n');
        editor.setData('<object>Hello</object>');
        same(editor.getData(),
            '<p>\n\tHello</p>\n');
    });
    test("Strip unwanted attributes", function(){
        editor.setData('<p style="color: blue;">Hello</p>');
        same(editor.getData(),
            '<p>\n\tHello</p>\n');
    });
}
