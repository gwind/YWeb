WTForms
========


自动生成 HTML
----------------

例如一个登录 form：

.. code-block:: html

    <form method="POST">${ xsrf_form_html() }
      % for field in form:
      ${ field.label }
      ${ field }
      % if field.errors:
      <ul class="text-danger">
        % for error in field.errors:
        <li>${ error }</li>
        % endfor
      </ul>
      % endif
      % endfor
      <button type="submit">${ _("Sign In") }</button>
    </form>


自定义 Field 渲染
--------------------

对于 class 参数，需要使用 **class_** 代替 ::

  form.user( class_="form-control", placeholder="Username/Email/UID")

