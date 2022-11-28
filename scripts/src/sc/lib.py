import codecs
import csv
import logging
from logging import NullHandler

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import warnings
import re

import pkg_resources

warnings.filterwarnings('ignore')


def calcTotal(all):
    bitKeys = list(filter(lambda x: "BitString" in x, all.columns.values))
    all['Total_Covered_Goals'] = 0
    all['Total_All_Goals'] = 0
    newKeys = []
    for bk in bitKeys:
        newKey = bk.replace('BitString', 'Goals')
        ak = newKey + 'All'
        ck = bk.replace('BitString', '')
        all[newKey] = all[bk].map(lambda c: str(c).count('1'))
        all[ak] = all[bk].map(lambda c: len(str(c)) if ck != 'ExceptionCoverage' else 1 + len(str(c)))
        all[ck] = all[newKey] / all[ak]
        all['Total_Covered_Goals'] += all[newKey]
        all['Total_All_Goals'] += all[ak]
        newKeys.append(newKey)
        newKeys.append(ck)
    newKeys.append('Total_Covered_Goals')
    newKeys.append('Size')
    newKeys.append('Length')
    return all, newKeys


def ana(s, key='Total_Covered_Goals'):
    mean_covered_goals = s.mean()[key]
    std_covered_goals = s.std()[key]
    max_covered_goals = s.max()[key]
    min_covered_goals = s.min()[key]
    return mean_covered_goals, std_covered_goals, max_covered_goals, min_covered_goals


def total(*sl):
    total_max = 0
    total_mean = 0
    for s in sl:
        tm, ts, t_max, t_min = ana(s)
        total_max += t_max
        total_mean += tm
    return total_max, total_mean


def compareSingle(n, m):
    if n > m:
        return 1
    elif n == m:
        return 0.5
    return 0


def get_single_a12_function(series):
    return lambda n: series.map(lambda m: compareSingle(n, m))


def cal_a12(a, b, key='Total_Covered_Goals'):
    c = pd.DataFrame({'a': a[key][:], 'b': b[key][:]})
    return c['a'].map(get_single_a12_function(c['b'])).sum().sum() / (a[key].count() * b[key].count())


def greater_possibility(a, b):
    ic = 0
    for ia in a:
        for ib in b:
            if ia > ib:
                ic = ic + 1
    return ic / float(len(a) * len(b))


def real_mu(a, b):
    return greater_possibility(a, b) - greater_possibility(b, a)


def calc_dij(a, b):
    if a > b:
        return 1
    elif a < b:
        return -1
    return 0


def calc_d(a, b):
    ic = 0
    for ia in a:
        for ib in b:
            ic += calc_dij(ia, ib)
    return ic / float(len(a) * len(b))


def calc_d_i(ia, b):
    ic = 0
    for ib in b:
        ic += calc_dij(ia, ib)
    return ic / float(len(b))


def real_sd_square(a, b):
    t = 0
    d = calc_d(a, b)

    for ia in a:
        t += len(b) ** 2 * ((calc_d_i(ia, b) - d) ** 2)
    for ib in b:
        t += len(a) ** 2 * (((0 - calc_d_i(ib, a)) - d) ** 2)
    for ia in a:
        for ib in b:
            t += ((calc_dij(ia, ib) - d) ** 2)
    if t == 0:
        t = 0.0000000000001  # avoid 0
    return t / float(len(a) * len(b) * (len(a) - 1) * (len(b) - 1))


def calc_t(a, b):
    s_square = real_sd_square(a, b)
    sd = math.sqrt(s_square)
    if sd == 0:
        return -1
    return (calc_d(a, b)) / sd


def calc_t_greater(a, b):
    s_square = real_sd_square(a, b)
    sd = math.sqrt(s_square)
    return (calc_d(a, b) - 1) / sd


def get_a_b(a, b, key):
    return a[key], b[key]


def get_z(all_data, a1, a2, key):
    a, b = get_a_b(all_data[a1], all_data[a2], key)
    ic = calc_t(a, b)
    if ic == -1:
        ic = 0
        print("something wrong with", a1, a2, key)
    return ic


def get_a12_stat(dft, all_data, remove_nom=False, zp=1.8409):  # p=0.05
    ret = {}
    dret = {}
    nk = list(all_data.keys())
    for index, v in dft.items():
        dret[index] = {}
        for vi, vv in v.iterrows():
            if not ret.__contains__(vi):
                ret[vi] = 0
            if not dret[index].__contains__(vi):
                dret[index][vi] = 0
            for ag in nk:
                if vv[ag] > 0.5:
                    if remove_nom and get_z(all_data, vi, ag, index) < zp:
                        continue
                    ret[vi] = ret[vi] + 1
                    dret[index][vi] = dret[index][vi] + 1
    return ret, dret


def calcResult(normal, deep, newKeys, nn='normal', dn='deep'):
    nn = str(nn)
    dn = str(dn)
    result = pd.DataFrame(columns=('type', dn + '_avg', nn + '_avg', 'a12', 'increase', 'p_value<=0.05'))
    i = 0
    for newKey in newKeys:
        deep_avg, deep_std, deep_max, deep_min = ana(deep, newKey)
        normal_avg, normal_std, normal_max, normal_min = ana(normal, newKey)
        a12 = cal_a12(deep, normal, newKey)
        sa, sb = get_a_b(deep, normal, newKey)
        result.loc[i] = [newKey, deep_avg, normal_avg, a12, (deep_avg - normal_avg) / normal_avg,
                         calc_t(sa, sb) > 1.8409]
        i = i + 1
    return result


def get_part(mne_all, number=30, delete_number=30):
    mne_deep = mne_all.head(number)
    mne_all = mne_all.drop(list(range(delete_number))).reset_index(drop=True)
    return mne_deep, mne_all


def get_all(file):
    mne_all = pd.read_csv(file)
    mne_all, mne_newKeys = calcTotal(mne_all)
    return mne_all, mne_newKeys


def get_data_matrix(group, newKeys):
    nl = len(group)
    gk = list(group.keys())
    gk.sort()
    agroup = list(map(lambda x: group[x], gk))

    a = {}
    for i in range(nl):
        a[gk[i]] = {}
        for j in range(0, nl):
            a[gk[i]][gk[j]] = calcResult(agroup[j], agroup[i], newKeys, gk[i], gk[j])
            a[gk[i]][gk[j]].index = a[gk[i]][gk[j]]['type']
            del a[gk[i]][gk[j]]['type']
    dft = {}
    for nk in newKeys:
        df = pd.DataFrame([], index=gk)
        for i in range(nl):
            sg = {}
            for j in range(nl):
                sg[gk[j]] = (a[gk[i]][gk[j]]['a12'][nk])
            df[gk[i]] = pd.Series(sg)
        dft[nk] = df
    for gk in newKeys:
        dft[gk] = dft[gk].T
        ml = []
        sl = []
        for key in list(dft[gk].index):
            ml.append(group[key].mean()[gk])
            sl.append(group[key].std()[gk])
        dft[gk].insert(0, 'std', sl)
        dft[gk].insert(0, 'mean', ml)
        dft[gk] = dft[gk].sort_values(by="mean", ascending=False)
    return a, dft


def draw_time_plot(group, newKeys, sg=None, sl=10):
    ag = {}
    for key in newKeys:
        sub = {}
        for w, data in group.items():
            sub[w], _, _, _ = ana(data, key)
        ag[key] = sub
    fig = plt.figure(figsize=(20, 9))
    i = 1
    for nk in newKeys:
        ax1 = fig.add_subplot(math.ceil(len(newKeys) / 2), 2, i)
        keys = list(ag[nk].keys())
        keys.sort()
        values = list(map(lambda x: ag[nk][x], keys))
        if sg is None:
            ax1.plot(keys, values, label=nk)
        else:
            gn = len(sg)
            b = 0
            e = sl
            for j in range(gn):
                ax1.plot(list(map(lambda x: x - b, keys[b:e])), values[b:e], label=sg[j] + "_" + nk)
                b = b + sl
                e = e + sl
        ax1.legend(loc='best')
        i = i + 1


def load_order(reports_dir):
    order_file = os.path.join(reports_dir, "order.csv")
    if not os.path.isfile(order_file):
        return None
    single_data = pd.read_csv(order_file)
    r = single_data["order"].to_list()
    r = list(map(lambda x: str(x), r))
    return r


def store_order(reports_dir, order_list):
    sr = pd.DataFrame({"order": order_list})
    sr.to_csv(os.path.join(reports_dir, "order.csv"), index=False)


def read_exp_data(exp_dir):
    fs = os.listdir(exp_dir)
    ds = {}
    for f in fs:
        sf = os.path.join(exp_dir, f)
        if not os.path.isdir(sf):
            continue
        if not f.startswith("task-"):
            continue
        f_parts = f.split("-")
        ds[int(f_parts[1])] = sf
    tasks = {}
    for task_id, d in ds.items():
        results_dir = os.path.join(d, "results")
        rs = os.listdir(results_dir)
        task_name = ""
        for r in rs:
            rf = os.path.join(results_dir, r)
            if os.path.isdir(rf):
                task_name = r
                break
        tasks[task_id] = {"name": task_name, "classes": [], "origin": ("task-%s" % task_id), "data": {}}
        task_dir = os.path.join(d, "results", task_name)
        projects = os.listdir(task_dir)
        for project in projects:
            pf = os.path.join(task_dir, project)
            if not os.path.isdir(pf):
                continue
            cs = os.listdir(pf)
            for single_class in cs:
                cf = os.path.join(pf, single_class)
                if not os.path.isdir(cf):
                    continue
                reports_dir = os.path.join(cf, "reports")
                if not os.path.isdir(reports_dir):
                    print("no report dir:", reports_dir)
                    continue
                tasks[task_id]['classes'].append([project, single_class])
                reports = os.listdir(reports_dir)
                order_list = load_order(reports_dir)
                if order_list is not None:
                    reports = order_list
                else:
                    reports.sort()
                task_data = None
                for single_report in reports:
                    if not single_report.isnumeric():
                        continue
                    statistics_file = os.path.join(reports_dir, single_report, "statistics.csv")
                    if not os.path.isfile(statistics_file):
                        print("no statistics.csv:", statistics_file)
                        continue
                    single_data = pd.read_csv(statistics_file)
                    if task_data is None:
                        task_data = single_data
                    else:
                        task_data = pd.concat([task_data, single_data], axis=0, ignore_index=True)
                tasks[task_id]['data'][single_class] = task_data
    return tasks


def remain_part(data, remain_total):
    for task_id, task in data.items():
        for class_name, single_data in task['data'].items():
            if single_data.count()['TARGET_CLASS'] > remain_total:
                _, single_data = get_part(single_data, single_data.count()['TARGET_CLASS'] - remain_total,
                                          single_data.count()['TARGET_CLASS'] - remain_total)
                data[task_id]['data'][class_name] = single_data
    return data


def calc_class_info(all):
    bitKeys = list(filter(lambda x: "BitString" in x, all.columns.values))
    all['Total_All_Goals'] = 0
    newKeys = ['Total_All_Goals']
    for bk in bitKeys:
        newKey = bk.replace('BitString', '')
        all[newKey] = all[bk].map(lambda c: len(str(c)))
        all['Total_All_Goals'] += all[newKey]
        newKeys.append(newKey)
    return all, newKeys


def get_all_class_info(origin_hadoop_data):
    nk = None
    stat_map = None
    for index in origin_hadoop_data.keys():
        class_data_map = {}
        for class_name, data in origin_hadoop_data[index]['data'].items():
            sd, nk = calc_class_info(data)
            if stat_map is None:
                stat_map = sd
            else:
                stat_map = pd.concat([stat_map, sd], axis=0, ignore_index=True)
    return stat_map, nk


def get_dir_class_info(path):
    origin_hadoop_data = read_exp_data(path)
    origin_hadoop_data = remain_part(origin_hadoop_data, 1)
    stat_map, nk = get_all_class_info(origin_hadoop_data)
    return stat_map, nk


def save_class_info(stat_map, nk, project, name):
    stat_map['project'] = project
    columns = ['project', 'TARGET_CLASS']
    columns.extend(nk)
    header = ['project', 'class']
    header.extend(nk)
    stat_map.to_csv('%s.csv' % name, index=False, columns=columns, header=header)


def init_class_info(file='share/data/artifacts/source_classes.csv'):
    source_classes_stream = pkg_resources.resource_stream("sc", file)
    d = pd.read_csv(source_classes_stream)
    return d


def get_data_by_branch_range(a, b=50, e=200, file='share/data/artifacts/source_classes.csv'):
    source_class_info = init_class_info(file)
    source_class_info = source_class_info[(source_class_info["n.branch"] >= b) & (source_class_info['n.branch'] < e)]
    r = a[a["class"].isin(source_class_info["class"])]
    return r


def get_smaller_class(b=50, e=200, file='share/data/artifacts/source_classes.csv'):
    source_class_info = init_class_info(file)
    source_class_info = source_class_info[(source_class_info["n.branch"] >= b) & (source_class_info['n.branch'] < e)]
    r = list(source_class_info["class"].to_dict().values())
    return r


def get_big_class():
    return get_smaller_class(200, 10000000000)


def get_better_cases(show_df, key, a, b):
    r = show_df[
        (show_df['%s-%s' % (key, a)] > show_df['%s-%s' % (key, b)]) & (show_df['%s-p-%s-%s' % (key, a, b)] > 0.5) & (
                show_df['%s-s-%s-%s' % (key, a, b)] == 1)]
    r = r[
        ['class_name', "%s-%s" % (key, a), "%s-%s" % (key, b), '%s-p-%s-%s' % (key, a, b), '%s-s-%s-%s' % (key, a, b)]]
    r["diff"] = r['%s-%s' % (key, a)] - r['%s-%s' % (key, b)]
    r["diff_rate"] = r["diff"] / (r['%s-%s' % (key, b)])
    r[r["diff_rate"] == float("inf")]['diff_rate'] = np.nan
    return r


def get_better_multi(show_df, nk, a, b):
    result = {}
    base_columns = {"key": [], a: [], b: []}
    df = pd.DataFrame(base_columns)
    for key in nk:
        result[key] = {}
        result[key][a] = get_better_cases(show_df, key, a, b)
        result[key][b] = get_better_cases(show_df, key, b, a)
        tmp = {"key": key, a: result[key][a].count()['class_name'], b: result[key][b].count()['class_name'],
               "non-significant":
                   show_df.count()['class_name'] - result[key][a].count()['class_name'] - result[key][b].count()[
                       'class_name']}
        df = df.append(tmp, ignore_index=True)
    return result, df


def get_compare_data(data_group_by_class, groups):
    if (len(groups) != 2):
        return False, False, False, False
    stat_map = {}
    nk = None
    for class_name in data_group_by_class.keys():
        class_data_map = {}
        all_config_keys = list(data_group_by_class[class_name].keys())
        class_sat = True
        for ck in groups:
            if not ck in all_config_keys:
                class_sat = False
                break
        if not class_sat:
            continue
        for ok, single_data in data_group_by_class[class_name].items():
            if ok in groups:
                group = groups[ok]
                class_data_map[group], nk = calcTotal(single_data['data'][class_name])
        a, dft = get_data_matrix(class_data_map, nk)
        stat_map[class_name] = [a, dft, class_data_map]
    base_columns = {"class_name": []}
    for k in nk:
        for _, v in groups.items():
            base_columns['%s-%s' % (k, v)] = []
    show_df = pd.DataFrame(base_columns)
    for class_name, s in stat_map.items():
        class_data_map = s[2]
        tmp_key = list(data_group_by_class[class_name].keys())[0]
        class_real_name = data_group_by_class[class_name][tmp_key]["data"][class_name]["TARGET_CLASS"][0]
        tmp = {'class_name': class_name, "class": class_real_name}
        for k in nk:
            for _, v in groups.items():
                tmp['%s-%s' % (k, v)] = s[1][k]['mean'][v]
                for _, v1 in groups.items():
                    if v == v1:
                        continue
                    if False:
                        p = 0.5
                        r = 0
                    else:
                        p = s[1][k][v1][v]
                        if p > 0.5:
                            r = get_z(class_data_map, v, v1, k)
                            r = 1 if r > 1.8409 else 0
                        else:
                            r = 0
                    tmp['%s-p-%s-%s' % (k, v, v1)] = p
                    tmp['%s-s-%s-%s' % (k, v, v1)] = r
        show_df = show_df.append(tmp, ignore_index=True)
        group_list = list(groups.values())
        ba, bd = get_better_multi(show_df, nk, group_list[0], group_list[1])
    return nk, show_df, ba, bd, stat_map


def get_mean_data_of_diff_rate(d):
    return d.describe().transpose()[["mean"]]


def get_stat_data_of_diff_rate(d):
    return d.describe().transpose()[["mean", "50%", "max"]]


def get_diff_rate_data(all_data, keys, config_name):
    data = None
    ck = []
    for key in keys:
        tmp = all_data[key][config_name][["class_name", "diff_rate"]]
        new_key = key
        dk = "%s_diff_rate" % new_key
        ck.append(dk)
        tmp = tmp.rename(columns={"diff_rate": dk})
        if data is None:
            data = tmp
        else:
            data = pd.merge(data, tmp, on='class_name', how='outer')
    return data[ck]


def analysis_overview(sd, rq4, analysis_keys=None):
    if analysis_keys is None:
        analysis_keys = pd.Series(
            ['BranchCoverage', 'WeakMutationCoverage', 'LineCoverage', 'MethodCoverage', 'MethodNoExceptionCoverage',
             'CBranchCoverage', 'ExceptionCoverageGoals', 'OutputCoverage'])
    ret_analysis_overview = sd[sd['key'].isin(analysis_keys)]
    cm = get_criteria_map(rq4)
    ret_analysis_overview['key'] = ret_analysis_overview['key'].apply(lambda x: cm[x])
    return ret_analysis_overview


def constituent_map(algorithm):
    return {
        ("con-branch-%s-1.2.0" % algorithm): "BranchCoverageBitString",
        ("con-wm-%s-1.2.0" % algorithm): "WeakMutationCoverageBitString",
        ("con-line-%s-1.2.0" % algorithm): "LineCoverageBitString",
        ("con-method-%s-1.2.0" % algorithm): "MethodCoverageBitString",
        ("con-methodne-%s-1.2.0" % algorithm): "MethodNoExceptionCoverageBitString",
        ("con-cbranch-%s-1.2.0" % algorithm): "CBranchCoverageBitString",
        ("con-exce-%s-1.2.0" % algorithm): "ExceptionCoverageBitString",
        ("con-output-%s-1.2.0" % algorithm): "OutputCoverageBitString"
    }


def concat_constituent_one_class(algorithm, data_group_by_class, a_class):
    m = constituent_map(algorithm)
    g = []
    i = 0
    for k, v in m.items():
        if i == 0:
            g.append(data_group_by_class[a_class][k]["data"][a_class])
        else:
            g.append(data_group_by_class[a_class][k]["data"][a_class][v])
        new_value = v.replace('BitString', '')
        size_slice = data_group_by_class[a_class][k]["data"][a_class]["Size"].copy()
        size_slice = size_slice.rename("Constituent" + new_value + "Size")
        g.append(size_slice)
        i = i + 1
    return pd.concat(g, axis=1)


def concat_constituent_all(algorithm, data_group_by_class):
    for ac in list(data_group_by_class.keys()):
        is_full = True
        ks = constituent_map(algorithm)
        for k, _ in ks.items():
            if not k in data_group_by_class[ac]:
                is_full = False
                break
        if not is_full:
            continue
        data_group_by_class[ac]["constituent-%s" % algorithm] = {}
        data_group_by_class[ac]["constituent-%s" % algorithm]["classes"] = \
            data_group_by_class[ac]["origin-%s-1.2.0" % algorithm]["classes"]
        data_group_by_class[ac]["constituent-%s" % algorithm]["data"] = {}
        data_group_by_class[ac]["constituent-%s" % algorithm]["data"][ac] = \
            concat_constituent_one_class(algorithm, data_group_by_class, ac)
        data_group_by_class[ac]["constituent-%s" % algorithm]["name"] = "constituent-%s" % algorithm
    return data_group_by_class


def get_criteria(rq4):
    criteria = ["BranchCoverage", "WeakMutationCoverage", "LineCoverage", "MethodCoverage", "MethodNoExceptionCoverage",
                "CBranchCoverage", "ExceptionCoverageGoals", "OutputCoverage"]
    if rq4:
        criteria.append("SelectedLineCoverage")
        criteria.append("SelectedWeakMutationCoverage")
    return criteria


def get_means(sdf, algorithm, rq4):
    criteria = get_criteria(rq4)
    ks = []
    for c in criteria:
        ks.append(c + "-" + algorithm)
    return sdf[ks].mean()


def get_size_means(sdf, algorithm, rq4):
    criteria = ['Size']
    ks = []
    for c in criteria:
        ks.append(c + "-" + algorithm)
    return sdf[ks].mean()


def get_criteria_map(rq4):
    criteria_map = {"BranchCoverage": "BC", "WeakMutationCoverage": "WM", "LineCoverage": "LC",
                    "MethodCoverage": "TMC", "MethodNoExceptionCoverage": "NTMC",
                    "CBranchCoverage": "DBC", "ExceptionCoverageGoals": "EC", "OutputCoverage": "OC"}
    if rq4:
        criteria_map["SelectedLineCoverage"] = "Selected Line"
        criteria_map["SelectedWeakMutationCoverage"] = "Selected Mutation"
    return criteria_map


def get_mean_table(sc_df, origin_df, constituent_df, means_func=None, cm=None):
    rq4 = False
    if means_func is None:
        means_func = get_means
    origin_means = means_func(origin_df, "original combination", rq4)
    sc_means = means_func(sc_df, "smart selection", rq4)
    constituent_means = means_func(constituent_df, "constituent criterion", rq4)
    if cm is None:
        cm = get_criteria_map(rq4)
    all_data = {"approach": ["smart selection", "original combination", "constituent criterion"]}
    for k, v in cm.items():
        item = [sc_means[k + "-" + all_data["approach"][0]], origin_means[k + "-" + all_data["approach"][1]],
                constituent_means[k + "-" + all_data["approach"][2]]]
        all_data[v] = item
    return pd.DataFrame(all_data)


def get_mean_table_4_size(sc_df, origin_df, constituent_data):
    rq4 = False
    cm = {"Size": "Size"}
    origin_means = get_size_means(origin_df, "original combination", rq4)
    sc_means = get_size_means(sc_df, "smart selection", rq4)
    all_data = {"approach": ["smart selection", "original combination", "BC", "WM",
                             "LC", "TMC", "NTMC", "DBC", "EC", "OC"]}
    for k, v in cm.items():
        item = [sc_means[k + "-" + all_data["approach"][0]], origin_means[k + "-" + all_data["approach"][1]]]
        begin_index = 2
        while begin_index < len(all_data['approach']):
            item.append(constituent_data[all_data['approach'][begin_index]])
            begin_index = begin_index + 1
        all_data[v] = item
    return pd.DataFrame(all_data)


def get_constituent_mean(dgc, algorithm, class_list=None):
    criterion_map = {
        "BC": "ConstituentBranchCoverageSize", "WM": "ConstituentWeakMutationCoverageSize",
        "LC": "ConstituentLineCoverageSize", "TMC": "ConstituentMethodCoverageSize",
        "NTMC": "ConstituentMethodNoExceptionCoverageSize", "DBC": "ConstituentCBranchCoverageSize",
        "EC": "ConstituentExceptionCoverageSize", "OC": "ConstituentOutputCoverageSize"
    }
    total_count = 0
    total_sum_dict = {}
    for ck in criterion_map.keys():
        total_sum_dict[ck] = 0
    for class_name, data in dgc.items():
        real_class_name = data["constituent-%s" % algorithm]['data'][class_name]['TARGET_CLASS'][0]
        if class_list is not None and real_class_name not in class_list:
            continue
        cd = data["constituent-%s" % algorithm]['data'][class_name]
        sum_dict = cd.sum().to_dict()
        total_count = total_count + len(cd)
        for ck in criterion_map.keys():
            total_sum_dict[ck] = total_sum_dict[ck] + sum_dict[criterion_map[ck]]
    total_mean_dict = {}
    for ck, cv in total_sum_dict.items():
        total_mean_dict[ck] = cv / total_count
    return total_mean_dict


def get_remain_by_name(name):
    d1 = {"con-branch-10-dynamosa-1.2.0": 5,
          "con-branch-10-mosa-1.2.0": 5,
          "con-branch-10-suite-1.2.0": 5,
          "con-branch-5-dynamosa-1.2.0": 10,
          "con-branch-5-mosa-1.2.0": 10,
          "con-branch-5-suite-1.2.0": 10,
          "con-branch-8-dynamosa-1.2.0": 10,
          "con-branch-8-mosa-1.2.0": 10,
          "con-branch-8-suite-1.2.0": 10,
          "con-cbranch-10-dynamosa-1.2.0": 5,
          "con-cbranch-10-mosa-1.2.0": 5,
          "con-cbranch-10-suite-1.2.0": 5,
          "con-cbranch-5-dynamosa-1.2.0": 10,
          "con-cbranch-5-mosa-1.2.0": 10,
          "con-cbranch-5-suite-1.2.0": 10,
          "con-cbranch-8-dynamosa-1.2.0": 10,
          "con-cbranch-8-mosa-1.2.0": 10,
          "con-cbranch-8-suite-1.2.0": 10,
          "con-exce-10-dynamosa-1.2.0": 5,
          "con-exce-10-mosa-1.2.0": 5,
          "con-exce-10-suite-1.2.0": 5,
          "con-exce-5-dynamosa-1.2.0": 10,
          "con-exce-5-mosa-1.2.0": 10,
          "con-exce-5-suite-1.2.0": 10,
          "con-exce-8-dynamosa-1.2.0": 10,
          "con-exce-8-mosa-1.2.0": 10,
          "con-exce-8-suite-1.2.0": 10,
          "con-line-10-dynamosa-1.2.0": 5,
          "con-line-10-mosa-1.2.0": 5,
          "con-line-10-suite-1.2.0": 5,
          "con-line-5-dynamosa-1.2.0": 10,
          "con-line-5-mosa-1.2.0": 10,
          "con-line-5-suite-1.2.0": 10,
          "con-line-8-dynamosa-1.2.0": 10,
          "con-line-8-mosa-1.2.0": 10,
          "con-line-8-suite-1.2.0": 10,
          "con-method-10-dynamosa-1.2.0": 5,
          "con-method-10-mosa-1.2.0": 5,
          "con-method-10-suite-1.2.0": 5,
          "con-method-5-dynamosa-1.2.0": 10,
          "con-method-5-mosa-1.2.0": 10,
          "con-method-5-suite-1.2.0": 10,
          "con-method-8-dynamosa-1.2.0": 10,
          "con-method-8-mosa-1.2.0": 10,
          "con-method-8-suite-1.2.0": 10,
          "con-methodne-10-dynamosa-1.2.0": 5,
          "con-methodne-10-mosa-1.2.0": 5,
          "con-methodne-10-suite-1.2.0": 5,
          "con-methodne-5-dynamosa-1.2.0": 10,
          "con-methodne-5-mosa-1.2.0": 10,
          "con-methodne-5-suite-1.2.0": 10,
          "con-methodne-8-dynamosa-1.2.0": 10,
          "con-methodne-8-mosa-1.2.0": 10,
          "con-methodne-8-suite-1.2.0": 10,
          "con-output-10-dynamosa-1.2.0": 5,
          "con-output-10-mosa-1.2.0": 5,
          "con-output-10-suite-1.2.0": 5,
          "con-output-5-dynamosa-1.2.0": 10,
          "con-output-5-mosa-1.2.0": 10,
          "con-output-5-suite-1.2.0": 10,
          "con-output-8-dynamosa-1.2.0": 10,
          "con-output-8-mosa-1.2.0": 10,
          "con-output-8-suite-1.2.0": 10,
          "con-wm-10-dynamosa-1.2.0": 5,
          "con-wm-10-mosa-1.2.0": 5,
          "con-wm-10-suite-1.2.0": 5,
          "con-wm-5-dynamosa-1.2.0": 10,
          "con-wm-5-mosa-1.2.0": 10,
          "con-wm-5-suite-1.2.0": 10,
          "con-wm-8-dynamosa-1.2.0": 10,
          "con-wm-8-mosa-1.2.0": 10,
          "con-wm-8-suite-1.2.0": 10,
          "origin-10-dynamosa-1.2.0": 5,
          "origin-10-mosa-1.2.0": 5,
          "origin-10-suite-1.2.0": 5,
          "origin-5-dynamosa-1.2.0": 10,
          "origin-5-mosa-1.2.0": 10,
          "origin-5-suite-1.2.0": 10,
          "origin-8-dynamosa-1.2.0": 10,
          "origin-8-mosa-1.2.0": 10,
          "origin-8-suite-1.2.0": 10,
          "sc-10-dynamosa-sc-release1": 5,
          "sc-10-mosa-sc-release1": 5,
          "sc-10-suite-sc-release1": 5,
          "sc-5-dynamosa-sc-release1": 10,
          "sc-5-mosa-sc-release1": 10,
          "sc-5-suite-sc-release1": 10,
          "sc-8-dynamosa-sc-release1": 10,
          "sc-8-mosa-sc-release1": 10,
          "sc-8-suite-sc-release1": 10}
    if name in d1:
        return d1[name]
    return None


def get_data_group(path, data_group_by_class=None):
    data = read_exp_data(path)
    remain_total = 30
    data = remain_part(data, remain_total)
    if data_group_by_class is None:
        data_group_by_class = {}
    for task_id, single in data.items():
        if not single['classes'][0][1] in data_group_by_class:
            data_group_by_class[single['classes'][0][1]] = {}
        new_remain = get_remain_by_name(single['name'])
        if new_remain is not None:
            ds = {task_id: single}
            ds = remain_part(ds, new_remain)
            single = ds[task_id]
        data_group_by_class[single['classes'][0][1]][single['name']] = single
    return data_group_by_class


def analysis_data_4_alg_2_compare(algorithm, data_group_by_class, a, b, rq4):
    m = get_group_name(algorithm)

    aks = pd.Series(
        ['BranchCoverage', 'WeakMutationCoverage', 'LineCoverage', 'MethodCoverage', 'MethodNoExceptionCoverage',
         'CBranchCoverage', 'ExceptionCoverageGoals', 'OutputCoverage'])
    if rq4:
        aks = pd.Series(
            ['BranchCoverage', 'WeakMutationCoverage', 'LineCoverage', 'MethodCoverage', 'MethodNoExceptionCoverage',
             'CBranchCoverage', 'ExceptionCoverageGoals', 'OutputCoverage', "SelectedLineCoverage"
                , "SelectedWeakMutationCoverage"])
    nk, show_df, sa, sd, origin_data = get_compare_data(data_group_by_class, {m[a]: a, m[b]: b})
    ws_analysis_overview = analysis_overview(sd, rq4, aks)

    show_df_smaller = get_data_by_branch_range(show_df)
    _, smaller_sd = get_better_multi(show_df_smaller, nk, a, b)
    smaller_ws_analysis_overview = analysis_overview(smaller_sd, rq4, aks)

    show_df_bigger = get_data_by_branch_range(show_df, 200, 3000000000)
    _, bigger_sd = get_better_multi(show_df_bigger, nk, a, b)
    bigger_ws_analysis_overview = analysis_overview(bigger_sd, rq4, aks)
    return {"statistic": show_df, "overview": ws_analysis_overview,
            "overview_small_classes": smaller_ws_analysis_overview, "overview_big_classes": bigger_ws_analysis_overview,
            "statistic_small_classes": show_df_smaller, "statistic_big_classes": show_df_bigger}


def get_group_name(algorithm):
    m = {
        "original combination": ('origin-%s-1.2.0' % algorithm),
        "smart selection": ('sc-%s-sc-release1' % algorithm),
        "constituent criterion": ('constituent-%s' % algorithm),
        "smart selection without the subsumption strategy": ("sub-%s-1.2.0" % algorithm)
    }
    return m


def add_2_mm(mm, key, data):
    mm[key] = np.round(data, decimals=2)
    return mm


def analysis_data_4_alg(data_group_by_class, algorithm):
    data_group_by_class = concat_constituent_all(algorithm, data_group_by_class)
    aos = analysis_data_4_alg_2_compare(algorithm, data_group_by_class, "original combination", "smart selection",
                                        False)

    sc = analysis_data_4_alg_2_compare(algorithm, data_group_by_class, "smart selection", "constituent criterion",
                                       False)

    oc = analysis_data_4_alg_2_compare(algorithm, data_group_by_class, "original combination", "constituent criterion",
                                       False)

    constituent_mean_all = get_constituent_mean(data_group_by_class, algorithm)
    constituent_mean_small = get_constituent_mean(data_group_by_class, algorithm, get_smaller_class())
    constituent_mean_big = get_constituent_mean(data_group_by_class, algorithm, get_big_class())
    mean_overview = get_mean_table(aos["statistic"], aos["statistic"], oc["statistic"])
    small_mean_overview = get_mean_table(aos["statistic_small_classes"], aos["statistic_small_classes"],
                                         oc["statistic_small_classes"])
    big_mean_overview = get_mean_table(aos["statistic_big_classes"], aos["statistic_big_classes"],
                                       oc["statistic_big_classes"])
    mm = {"all": mean_overview, "small": small_mean_overview, "big": big_mean_overview}
    mm["all"] = np.round(mm["all"], decimals=2)
    mm["small"] = np.round(mm["small"], decimals=2)
    mm["big"] = np.round(mm["big"], decimals=2)
    mm = add_2_mm(mm, "all_size", get_mean_table_4_size(aos["statistic"], aos["statistic"], constituent_mean_all))

    mm = add_2_mm(mm, "small_size", get_mean_table_4_size(aos["statistic_small_classes"],
                                                          aos["statistic_small_classes"],
                                                          constituent_mean_small))

    mm = add_2_mm(mm, "big_size", get_mean_table_4_size(aos["statistic_big_classes"],
                                                        aos["statistic_big_classes"],
                                                        constituent_mean_big))

    return aos, sc, oc, mm


def get_mean_table_4_representative(sc_df, mean_func=None, cm=None):
    if mean_func is None:
        mean_func = get_means
    representative_means = mean_func(sc_df, "smart selection without the subsumption strategy", False)
    sc_means = mean_func(sc_df, "smart selection", False)
    if cm is None:
        cm = get_criteria_map(False)
    all_data = {"approach": ["smart selection", "smart selection without the subsumption strategy"]}
    for k, v in cm.items():
        item = [sc_means[k + "-" + all_data["approach"][0]], representative_means[k + "-" + all_data["approach"][1]]]
        all_data[v] = item
    return pd.DataFrame(all_data)


def analysis_data_4_representative(data_group_by_class, algorithm):
    aos = analysis_data_4_alg_2_compare(algorithm, data_group_by_class,
                                        "smart selection without the subsumption strategy", "smart selection",
                                        False)
    mean_overview = get_mean_table_4_representative(aos["statistic"])
    small_mean_overview = get_mean_table_4_representative(aos["statistic_small_classes"])
    big_mean_overview = get_mean_table_4_representative(aos["statistic_big_classes"])
    mm = {"all": mean_overview, "small": small_mean_overview, "big": big_mean_overview}
    mm["all"] = np.round(mm["all"], decimals=2)
    mm["small"] = np.round(mm["small"], decimals=2)
    mm["big"] = np.round(mm["big"], decimals=2)

    size_map = {"Size": "Size"}
    mm = add_2_mm(mm, "all_size", get_mean_table_4_representative(aos["statistic"], get_size_means, size_map))

    mm = add_2_mm(mm, "small_size", get_mean_table_4_representative(aos["statistic_small_classes"],
                                                                    get_size_means, size_map))

    mm = add_2_mm(mm, "big_size", get_mean_table_4_representative(aos["statistic_big_classes"],
                                                                  get_size_means, size_map))

    return aos, mm


def write_data_4_representative(suite_os, suite_mean_overview, alg, result_folder):
    ck = ["all", "small", "big"]
    for ick in ck:
        ick_suffix = "_" + ick
        if ick == "all":
            ick_suffix = ""
        suite_mean_overview[ick].to_csv(result_folder + "/sub_%s_mean_overview%s.csv" % (alg, ick_suffix), index=False)
        suite_mean_overview[ick + "_size"].to_csv(result_folder + "/sub_%s_mean_size_overview%s.csv" % (alg, ick_suffix)
                                                  , index=False)
    plot_bar_4_compare(suite_os["overview"], "%s_rs" % alg, result_folder)
    plot_bar_4_compare(suite_os["overview_small_classes"], "%s_rs_small_classes" % alg, result_folder)
    plot_bar_4_compare(suite_os["overview_big_classes"], "%s_rs_big_classes" % alg, result_folder)


def plot_bar_4_compare(data, save_name="", result_folder=""):
    color_map = {"original combination": '#7294cb', "smart selection": "green", "non-significant": "#F5F5F5",
                 "constituent criterion": "#e1944c", "smart selection without the subsumption strategy": "#286795"}
    data.plot.bar(x='key', stacked=True, color=color_map, edgecolor="black")
    if save_name != "":
        if result_folder == "":
            plt.savefig(save_name + ".pdf", bbox_inches='tight')
            data.to_csv(save_name + "_detail.csv", index=False)
        else:
            plt.savefig(result_folder + "/" + save_name + ".pdf", bbox_inches='tight')
            data.to_csv(result_folder + "/" + save_name + "_detail.csv", index=False)


def write_data(suite_os, suite_sc, suite_oc, suite_mean_overview, alg, result_folder):
    ck = ["all", "small", "big"]
    for ick in ck:
        ick_suffix = "_" + ick
        if ick == "all":
            ick_suffix = ""
        suite_mean_overview[ick].to_csv(result_folder + "/%s_mean_overview%s.csv" % (alg, ick_suffix), index=False)
        suite_mean_overview[ick + "_size"].to_csv(result_folder + "/%s_mean_size_overview%s.csv" % (alg, ick_suffix),
                                                  index=False)
    plot_bar_4_compare(suite_os["overview"], "%s_os" % alg, result_folder)
    plot_bar_4_compare(suite_os["overview_small_classes"], "%s_os_small_classes" % alg, result_folder)
    plot_bar_4_compare(suite_os["overview_big_classes"], "%s_os_big_classes" % alg, result_folder)
    plot_bar_4_compare(suite_sc["overview"], "%s_sc" % alg, result_folder)
    plot_bar_4_compare(suite_oc["overview"], "%s_oc" % alg, result_folder)


def ana_budget_one(data_group_by_class, alg, budget, result_folder):
    data_group_by_class = concat_constituent_all_4_budget(alg, data_group_by_class, budget)
    ana_budget_mean_to_disk(alg, budget, data_group_by_class, result_folder)
    ana_budget_mean_to_disk(alg, budget, data_group_by_class, result_folder, get_big_class(), 'big')
    ana_budget_mean_to_disk(alg, budget, data_group_by_class, result_folder, get_smaller_class(), 'small')


def ana_budget_mean_to_disk(alg, budget, data_group_by_class, result_folder, class_list=None, suffix=''):
    mean_con, con_total_summary = get_mean_4_budget_constituent(data_group_by_class, alg, budget, class_list)
    mean_ss, ss_total_summary = get_mean_4_budget_ss(data_group_by_class, alg, budget, class_list)
    mean_origin, origin_total_summary = get_mean_4_budget_origin(data_group_by_class, alg, budget, class_list)
    total_summary = {
        "constituent": con_total_summary,
        "ss": ss_total_summary,
        "origin": origin_total_summary
    }
    if suffix != '':
        suffix = '_' + suffix
    for k, v in total_summary.items():
        df = pd.DataFrame([v])
        df.to_csv(os.path.join(result_folder, "%s_budget_mean_total_%d_%s%s.csv" % (alg, budget, k, suffix)),
                  index=False)

    df = pd.DataFrame([mean_ss, mean_origin, mean_con])
    df.to_csv(os.path.join(result_folder, "%s_budget_mean_%d%s.csv" % (alg, budget, suffix)), index=False)
    ad, mean_total = get_mean_size_4_budget(data_group_by_class, alg, budget, class_list)
    aks = list(ad.keys())
    avs = []
    for ak in aks:
        avs.append(ad[ak])
    df = pd.DataFrame(data={"approach": aks, "Size": avs})
    df.to_csv(os.path.join(result_folder, "%s_budget_mean_size_%d%s.csv" % (alg, budget, suffix)), index=False)

    df = pd.DataFrame([mean_total])
    df.to_csv(os.path.join(result_folder, "%s_budget_mean_size_total_%d%s.csv" % (alg, budget, suffix)), index=False)


def ana_budget(data_group_by_class, alg, result_folder):
    budgets = [5, 8, 10]
    data_group_by_class = calc_coverage_4_budget(data_group_by_class, alg)
    for budget in budgets:
        ana_budget_one(data_group_by_class, alg, budget, result_folder)


def ana_rq123(data_group_by_class, result_folder, ags=None):
    if ags is None:
        ags = ["suite", "mosa", "dynamosa"]
    for ag in ags:
        suite_os, suite_sc, suite_oc, suite_mean_overview = analysis_data_4_alg(data_group_by_class, ag)
        write_data(suite_os, suite_sc, suite_oc, suite_mean_overview, ag, result_folder)
        ana_budget(data_group_by_class, ag, result_folder)


def ana_select(data_group_by_class, result_folder):
    selected_line_data = {"class": [], "all_line": [], "selected_line": [], "rate": []}
    config_key = "sc-suite-sc-release1"
    for name in data_group_by_class.keys():
        sn = data_group_by_class[name][config_key]["data"][name]["SelectedLineNumber"][0]
        line_all = data_group_by_class[name][config_key]["data"][name]["LineCoverageGoalsAll"][0]
        class_name = data_group_by_class[name][config_key]["data"][name]["TARGET_CLASS"][0]
        selected_line_data["class"].append(class_name)
        selected_line_data["all_line"].append(line_all)
        rate = sn / line_all
        if sn > line_all:
            rate = 0
            sn = 0
        selected_line_data["selected_line"].append(sn)
        selected_line_data["rate"].append(rate)
    selected_line_data = pd.DataFrame(selected_line_data)
    selected_line_data.to_csv(os.path.join(result_folder, "selected_line_data.csv"), index=False)


def add_sub_data(sub_data_group_by_class, sub_information, group, ag):
    m = get_group_name(ag)
    for k, v in sub_data_group_by_class.items():
        class_name = sub_data_group_by_class[k][m[group]]["data"][k]["TARGET_CLASS"][0]
        si = sub_information[class_name]
        line_keys = si[1].split(":")
        mutant_keys = si[2].split(":")
        if group == "smart selection":
            if int(sub_data_group_by_class[k][m[group]]["data"][k]["SelectedLineNumber"][0]) != len(line_keys):
                current_logger.error("%s line number not match %d %d" % (class_name,
                                                                         int(sub_data_group_by_class[k][m[group]][
                                                                                 "data"][k]["SelectedLineNumber"][0]),
                                                                         len(line_keys)))
            if int(sub_data_group_by_class[k][m[group]]["data"][k]["SelectedMutationNumber"][0]) != len(mutant_keys):
                current_logger.error("%s mutation number not match %d %d" % (class_name, int(sub_data_group_by_class[k]
                                                                                             [m[group]]["data"][k][
                                                                                                 "SelectedMutationNumber"][
                                                                                                 0]), len(mutant_keys)))
        sub_data_group_by_class = \
            add_selected_data("LineCoverageBitString", group, k, line_keys, m, "SelectedLineCoverageBitString",
                              "SelectedLineNumber", sub_data_group_by_class)
        sub_data_group_by_class = \
            add_selected_data("WeakMutationCoverageBitString", group, k, mutant_keys, m,
                              "SelectedWeakMutationCoverageBitString",
                              "SelectedMutationNumber", sub_data_group_by_class)

    return sub_data_group_by_class


def add_selected_data(bs, group, k, selected_keys, m, sbs, sn, sub_data_group_by_class):
    sub_data_group_by_class[k][m[group]]["data"][k][sbs] \
        = sub_data_group_by_class[k][m[group]]["data"][k][bs] \
        .map(create_selected_lambda(k, m[group], selected_keys))
    sbg = sbs.replace("BitString", "Goals")
    sbc = sbs.replace("BitString", "")
    sub_data_group_by_class[k][m[group]]["data"][k][sbg] \
        = sub_data_group_by_class[k][m[group]]["data"][k][sbs].map(lambda c: str(c).count('1'))
    if group != "smart selection":
        sub_data_group_by_class[k][m[group]]["data"][k][sn] \
            = sub_data_group_by_class[k][m[group]]["data"][k][sbs].map(lambda c: len(str(c)))
    sub_data_group_by_class[k][m[group]]["data"][k][sbc] \
        = sub_data_group_by_class[k][m[group]]["data"][k][sbg] \
          / sub_data_group_by_class[k][m[group]]["data"][k][sn]
    return sub_data_group_by_class


def get_default_logger():
    logger = logging.getLogger('sc')
    if not logger.handlers:
        logger.addHandler(NullHandler())
    return logger


current_logger = get_default_logger()


def set_logger(logger):
    global current_logger
    current_logger = logger


def select_fix_keys(s, class_name, group, keys):
    r = []
    if not isinstance(s, str):
        s = str(s)
        current_logger.info("%s not string" % s)
    for k in keys:
        k = int(k)
        if k >= len(s):
            r.append('0')
            current_logger.error("mutant out of bounds: %s,%s:%d" % (class_name, group, k))
        else:
            r.append(str(s[k]))
    return "".join(r)


def create_selected_lambda(cn, group, keys):
    return lambda x: select_fix_keys(x, cn, group, keys)


def ana_rq4(f3_data_group_by_class, sub_data_group_by_class, result_folder):
    sub_classes = get_result_sub_classes()
    filtered_sd = {}
    for k, v in sub_data_group_by_class.items():
        if k in sub_classes:
            filtered_sd[k] = v
    sub_data_group_by_class = filtered_sd
    for k, v in sub_data_group_by_class.items():
        for dk, dv in f3_data_group_by_class[k].items():
            sub_data_group_by_class[k][dk] = dv
    sub_information = get_all_sub_classes_information()
    ags = ["suite", "mosa", "dynamosa"]
    for ag in ags:
        # sub_data_group_by_class = add_sub_data(sub_data_group_by_class, sub_information, "smart selection", ag)
        # sub_data_group_by_class = add_sub_data(sub_data_group_by_class, sub_information, "smart selection without the subsumption strategy", ag)

        aos, mm = analysis_data_4_representative(sub_data_group_by_class, ag)
        write_data_4_representative(aos, mm, ag, result_folder)
    return sub_data_group_by_class


def get_all_sub_classes_information():
    config_file = pkg_resources.resource_stream("sc", 'share/data/artifacts/sub_info.csv')
    utf8_reader = codecs.getreader("utf-8")
    c = csv.DictReader(utf8_reader(config_file))
    sub_information = {}
    for record in c:
        sub_information[record["class"]] = [record['class'], record["SelectedLineString"],
                                            record["SelectedMutationString"]]
    return sub_information


def get_result_sub_classes():
    config_file = pkg_resources.resource_stream("sc", 'share/data/artifacts/rca.csv')
    utf8_reader = codecs.getreader("utf-8")
    c = csv.DictReader(utf8_reader(config_file))
    sub_information = {}
    for record in c:
        sub_information[record["ca"]] = record['ca']
    return sub_information


def constituent_map_4_budget(algorithm, budget):
    return {
        ("con-branch-%d-%s-1.2.0" % (budget, algorithm)): "BranchCoverageBitString",
        ("con-wm-%d-%s-1.2.0" % (budget, algorithm)): "WeakMutationCoverageBitString",
        ("con-line-%d-%s-1.2.0" % (budget, algorithm)): "LineCoverageBitString",
        ("con-method-%d-%s-1.2.0" % (budget, algorithm)): "MethodCoverageBitString",
        ("con-methodne-%d-%s-1.2.0" % (budget, algorithm)): "MethodNoExceptionCoverageBitString",
        ("con-cbranch-%d-%s-1.2.0" % (budget, algorithm)): "CBranchCoverageBitString",
        ("con-exce-%d-%s-1.2.0" % (budget, algorithm)): "ExceptionCoverageBitString",
        ("con-output-%d-%s-1.2.0" % (budget, algorithm)): "OutputCoverageBitString"
    }


def concat_constituent_one_class_4_budget(algorithm, data_group_by_class, a_class, budget):
    m = constituent_map_4_budget(algorithm, budget)
    g = []
    i = 0
    for k, v in m.items():
        new_value = v.replace('BitString', '')
        if k not in data_group_by_class[a_class]:
            current_logger.warning("%s not in %s %d %s", k, algorithm, budget, a_class)
            continue
        if i == 0:
            g.append(data_group_by_class[a_class][k]["data"][a_class])
        else:
            g.append(data_group_by_class[a_class][k]["data"][a_class][v])
            g.append(data_group_by_class[a_class][k]["data"][a_class][new_value])
        if v == 'ExceptionCoverageBitString':
            g.append(data_group_by_class[a_class][k]["data"][a_class]["ExceptionCoverageGoals"])
        size_slice = data_group_by_class[a_class][k]["data"][a_class]["Size"].copy()
        size_slice = size_slice.rename("Constituent" + new_value + "Size")
        g.append(size_slice)
        i = i + 1
    return pd.concat(g, axis=1)


def concat_constituent_all_4_budget(algorithm, data_group_by_class, budget=5):
    for ac in list(data_group_by_class.keys()):
        is_empty = True
        ks = constituent_map_4_budget(algorithm, budget)
        for k, _ in ks.items():
            if k in data_group_by_class[ac]:
                is_empty = False
                break
        if is_empty:
            continue
        data_group_by_class[ac]["constituent-%d-%s" % (budget, algorithm)] = {}
        data_group_by_class[ac]["constituent-%d-%s" % (budget, algorithm)]["classes"] = \
            data_group_by_class[ac]["origin-%s-1.2.0" % (algorithm)]["classes"]
        data_group_by_class[ac]["constituent-%d-%s" % (budget, algorithm)]["data"] = {}
        data_group_by_class[ac]["constituent-%d-%s" % (budget, algorithm)]["data"][ac] = \
            concat_constituent_one_class_4_budget(algorithm, data_group_by_class, ac, budget)
        data_group_by_class[ac]["constituent-%d-%s" % (budget, algorithm)]["name"] = "constituent-%d-%s" % (
            budget, algorithm)
    return data_group_by_class


def calc_coverage_4_budget(data_group_by_class, algorithm):
    groups = [re.compile('^sc-(\d+)-%s-sc-release1$' % algorithm), re.compile('^con-(.+)-(\d+)-%s-1.2.0$' % algorithm),
              re.compile('^origin-(\d+)-%s-1.2.0$' % algorithm)]
    for class_name in data_group_by_class.keys():
        for ok, single_data in data_group_by_class[class_name].items():
            match = False
            for rm in groups:
                if rm.match(ok) is not None:
                    match = True
                    break
            if match:
                calcTotal(single_data['data'][class_name])
    return data_group_by_class


def get_mean_4_budget_basic(cname, dgc, name, class_list=None):
    # criterion_map = {
    #    "BC": "ConstituentBranchCoverageSize", "WM": "ConstituentWeakMutationCoverageSize",
    #    "LC": "ConstituentLineCoverageSize", "TMC": "ConstituentMethodCoverageSize",
    #    "NTMC": "ConstituentMethodNoExceptionCoverageSize", "DBC": "ConstituentCBranchCoverageSize",
    #    "EC": "ConstituentExceptionCoverageSize", "OC": "ConstituentOutputCoverageSize"
    # }
    criterion_map = {
        "BC": "BranchCoverage", "WM": "WeakMutationCoverage",
        "LC": "LineCoverage", "TMC": "MethodCoverage",
        "NTMC": "MethodNoExceptionCoverage", "DBC": "CBranchCoverage",
        "EC": "ExceptionCoverageGoals", "OC": "OutputCoverage"
    }
    total_count_map = {}
    for k, _ in criterion_map.items():
        total_count_map[k] = 0
    total_sum_dict = {}
    for ck in criterion_map.keys():
        total_sum_dict[ck] = 0
    for class_name, data in dgc.items():
        if name not in data:
            continue
        real_class_name = data[name]['data'][class_name]['TARGET_CLASS'][0]
        if class_list is not None and real_class_name not in class_list:
            continue
        cd = data[name]['data'][class_name]
        sum_dict = cd.sum().to_dict()
        for ck in criterion_map.keys():
            if criterion_map[ck] not in sum_dict:
                continue
            total_count_map[ck] = total_count_map[ck] + len(cd)
            total_sum_dict[ck] = total_sum_dict[ck] + sum_dict[criterion_map[ck]]
    total_mean_dict = {"approach": cname}
    for ck, cv in total_sum_dict.items():
        total_count = total_count_map[ck]
        if total_count != 0:
            total_mean_dict[ck] = cv / total_count
    total_count_map["approach"] = cname
    return total_mean_dict, total_count_map


def get_mean_4_budget_constituent(dgc, algorithm, budget, class_list=None):
    return get_mean_4_budget_basic("constituent criterion", dgc, "constituent-%d-%s" % (budget, algorithm), class_list)


def get_mean_4_budget_ss(dgc, algorithm, budget, class_list=None):
    return get_mean_4_budget_basic("smart selection", dgc, "sc-%d-%s-sc-release1" % (budget, algorithm), class_list)


def get_mean_4_budget_origin(dgc, algorithm, budget, class_list=None):
    return get_mean_4_budget_basic("original combination", dgc, "origin-%d-%s-1.2.0" % (budget, algorithm), class_list)


def get_mean_size_4_budget(dgc, algorithm, budget, class_list=None):
    criterion_map = {
        "smart selection": ["sc-%d-%s-sc-release1" % (budget, algorithm), "Size"],
        "original combination": ["origin-%d-%s-1.2.0" % (budget, algorithm), "Size"],
        "BC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentBranchCoverageSize"],
        "WM": ["constituent-%d-%s" % (budget, algorithm), "ConstituentWeakMutationCoverageSize"],
        "LC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentLineCoverageSize"],
        "TMC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentMethodCoverageSize"],
        "NTMC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentMethodNoExceptionCoverageSize"],
        "DBC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentCBranchCoverageSize"],
        "EC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentExceptionCoverageSize"],
        "OC": ["constituent-%d-%s" % (budget, algorithm), "ConstituentOutputCoverageSize"]}
    total_count_dict = {}
    for k in criterion_map.keys():
        total_count_dict[k] = 0
    total_sum_dict = {}
    for ck in criterion_map.keys():
        total_sum_dict[ck] = 0
    for class_name, data in dgc.items():
        for ck, cv in criterion_map.items():
            if cv[0] not in data:
                continue
            real_class_name = data[cv[0]]['data'][class_name]['TARGET_CLASS'][0]
            if class_list is not None and real_class_name not in class_list:
                continue
            if cv[1] not in data[cv[0]]['data'][class_name]:
                continue
            cd = data[cv[0]]['data'][class_name]
            sum_dict = cd.sum().to_dict()
            total_count_dict[ck] = total_count_dict[ck] + len(cd)
            total_sum_dict[ck] = total_sum_dict[ck] + sum_dict[cv[1]]
    total_mean_dict = {}
    for ck, cv in total_sum_dict.items():
        total_count = total_count_dict[ck]
        if total_count != 0:
            total_mean_dict[ck] = cv / total_count
    return total_mean_dict, total_count_dict
